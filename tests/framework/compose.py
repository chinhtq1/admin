"""docker compose stack manager for system tests (project `emspoc`, file infra/docker-compose.yml).

Default mode is ATTACH-ONLY: tests use a stack that is already up and never start/stop/restart it.
Mutating operations (up, stop, start, restart, kill, down) require EMS_TEST_OWN_STACK=1, which only
the job/agent that owns the Docker stack sets (CI system job, the designated stack-owner agent).
Read-only operations (ps, logs) are always allowed and are used by the failure-artifact hook.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from framework import REPO_ROOT
from framework.wait import wait_for_value

COMPOSE_FILE = REPO_ROOT / "infra" / "docker-compose.yml"


class StackNotOwned(PermissionError):
    pass


@dataclass
class ComposeStack:
    project: str = "emspoc"
    compose_file: Path = COMPOSE_FILE
    env_file: Path | None = None

    @property
    def owned(self) -> bool:
        return os.environ.get("EMS_TEST_OWN_STACK") == "1"

    def _base(self) -> list[str]:
        cmd = ["docker", "compose", "-p", self.project, "-f", str(self.compose_file)]
        if self.env_file and self.env_file.is_file():
            cmd += ["--env-file", str(self.env_file)]
        return cmd

    def _run(self, *args: str, timeout: float = 120, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*self._base(), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
            cwd=self.compose_file.parent,
        )

    def _require_owner(self, action: str) -> None:
        if not self.owned:
            raise StackNotOwned(
                f"'{action}' on compose project {self.project!r} needs EMS_TEST_OWN_STACK=1 "
                "(only the Docker stack owner may change the stack)"
            )

    # ---- read-only ----------------------------------------------------------------------
    @staticmethod
    def docker_available() -> bool:
        if not shutil.which("docker"):
            return False
        try:
            return (
                subprocess.run(
                    ["docker", "info", "--format", "{{.ServerVersion}}"],
                    capture_output=True,
                    timeout=10,
                    check=False,
                ).returncode
                == 0
            )
        except (OSError, subprocess.TimeoutExpired):
            return False

    def ps(self) -> list[dict]:
        cp = self._run("ps", "--format", "json", check=False, timeout=30)
        if cp.returncode != 0 or not cp.stdout.strip():
            return []
        out = cp.stdout.strip()
        if out.startswith("["):
            return json.loads(out)
        return [json.loads(line) for line in out.splitlines() if line.strip()]

    def service_states(self) -> dict[str, str]:
        """{service: 'running (healthy)'...} from `docker compose ps`."""
        return {s.get("Service", "?"): f"{s.get('State', '')} {s.get('Health', '')}".strip() for s in self.ps()}

    def is_up(self, required: tuple[str, ...] = ("mosquitto", "db", "vsite", "bridge", "ingest")) -> bool:
        states = self.service_states()
        return all(states.get(s, "").startswith("running") and "unhealthy" not in states.get(s, "") for s in required)

    def logs(self, *services: str, since: str | None = None, tail: int | None = 2000) -> str:
        args = ["logs", "--no-color", "--timestamps"]
        if since:
            args += ["--since", since]
        if tail:
            args += ["--tail", str(tail)]
        cp = self._run(*args, *services, check=False, timeout=60)
        return cp.stdout + (f"\n[stderr]\n{cp.stderr}" if cp.stderr.strip() else "")

    # ---- mutating (owner only) -------------------------------------------------------------
    def up(self, *services: str, build: bool = False, timeout: float = 900) -> None:
        self._require_owner("up")
        args = ["up", "-d", "--wait", *(["--build"] if build else []), *services]
        self._run(*args, timeout=timeout)

    def stop(self, *services: str, timeout: float = 120) -> None:
        self._require_owner("stop")
        self._run("stop", *services, timeout=timeout)

    def start(self, *services: str, timeout: float = 300) -> None:
        self._require_owner("start")
        self._run("start", *services, timeout=timeout)

    def restart(self, *services: str, timeout: float = 300) -> None:
        self._require_owner("restart")
        self._run("restart", *services, timeout=timeout)

    def kill(self, *services: str, signal: str = "SIGKILL") -> None:
        self._require_owner("kill")
        self._run("kill", "-s", signal, *services)

    def wait_healthy(self, *services: str, timeout: float = 180) -> dict[str, str]:
        def healthy() -> dict[str, str]:
            return self.service_states()

        return wait_for_value(
            healthy,
            lambda st: all(
                "healthy" in st.get(s, "") or (st.get(s, "").startswith("running") and "health" not in st.get(s, ""))
                for s in services
            ),
            timeout=timeout,
            interval=1.0,
            desc=f"services healthy: {services}",
        )
