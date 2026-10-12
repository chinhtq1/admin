"""Test environment loading.

Precedence (highest first):
  1. process environment (CI sets these explicitly),
  2. infra/.env (git-ignored; the local emspoc stack was started with it),
  3. generated throw-away secrets (only for containers the test itself starts, e.g. testcontainers).

No secret value is ever stored in the repository or written unredacted to test-results/.
A generated secret cannot authenticate against the emspoc stack; `require_stack_credentials()`
fails fast with a clear message instead of producing confusing auth errors.
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

from framework import REPO_ROOT

ENV_FILE = REPO_ROOT / "infra" / ".env"

# Keys that hold secrets (names from infra/.env.example).
SECRET_KEYS = (
    "DB_PASSWORD",
    "MQTT_PASS_EDGE_VSITE01",
    "MQTT_PASS_EDGE_EV01",
    "MQTT_PASS_INGEST",
    "MQTT_PASS_DISPATCHER",
    "MQTT_PASS_HEALTH",
    "GRAFANA_ADMIN_PASSWORD",
)
# MQTT username -> env key of its password (usernames from infra/mosquitto/acl.conf).
MQTT_USERS = {
    "edge-vsite01": "MQTT_PASS_EDGE_VSITE01",
    "edge-ev01": "MQTT_PASS_EDGE_EV01",
    "ingest": "MQTT_PASS_INGEST",
    "dispatcher": "MQTT_PASS_DISPATCHER",
    "health": "MQTT_PASS_HEALTH",
}


def parse_env_file(path: Path) -> dict[str, str]:
    """Minimal KEY=VALUE parser (comments, blank lines, optional quotes). No interpolation."""
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        out[key] = value
    return out


@dataclass(frozen=True)
class TestEnv:
    __test__ = False  # not a test class

    values: dict[str, str]
    generated: frozenset[str] = field(default_factory=frozenset)
    source: str = "environment"

    # ---- generic access ---------------------------------------------------------------
    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)

    def secret(self, key: str) -> str:
        return self.values[key]

    def redacted(self) -> dict[str, str]:
        return {
            k: ("<generated>" if k in self.generated else "<set>") if k in SECRET_KEYS else v
            for k, v in sorted(self.values.items())
        }

    # ---- endpoints of the local stack (ports bound to 127.0.0.1 in docker-compose.yml) ----
    @property
    def compose_project(self) -> str:
        return self.values.get("COMPOSE_PROJECT_NAME", "emspoc")

    @property
    def mqtt_host(self) -> str:
        return self.values.get("EMS_MQTT_HOST", "127.0.0.1")

    @property
    def mqtt_port(self) -> int:
        return int(self.values.get("EMS_MQTT_PORT", "1883"))

    @property
    def vsite_url(self) -> str:
        return self.values.get("EMS_VSITE_URL", "http://127.0.0.1:8080")

    def db_dsn(self) -> str:
        """libpq keyword DSN (password not URL-encoded -> no breakage on '@:/')."""
        host = self.values.get("EMS_DB_HOST", "127.0.0.1")
        port = self.values.get("EMS_DB_PORT", "5432")
        name = self.values.get("EMS_DB_NAME", "ems")
        user = self.values.get("EMS_DB_USER", "ems")
        return f"host={host} port={port} dbname={name} user={user} password={self.secret('DB_PASSWORD')}"

    def mqtt_credentials(self, username: str) -> tuple[str, str]:
        return username, self.secret(MQTT_USERS[username])

    def require_stack_credentials(self) -> None:
        missing = [k for k in SECRET_KEYS if k in self.generated]
        if missing:
            raise RuntimeError(
                "System tests attach to the running emspoc stack and need its real credentials; "
                f"missing {missing}. Create infra/.env (cp infra/.env.example infra/.env) or export them."
            )


def load_test_env(environ: dict[str, str] | None = None, env_file: Path = ENV_FILE) -> TestEnv:
    environ = dict(os.environ if environ is None else environ)
    values = parse_env_file(env_file)
    source = "infra/.env" if values else "environment"
    values.update({k: v for k, v in environ.items() if k in SECRET_KEYS or k.startswith(("EMS_", "COMPOSE_"))})
    generated = set()
    for key in SECRET_KEYS:
        if not values.get(key):
            values[key] = secrets.token_hex(16)
            generated.add(key)
    return TestEnv(values=values, generated=frozenset(generated), source=source)
