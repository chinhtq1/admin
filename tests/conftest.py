"""Shared fixtures for every test level.

Product packages are importable through `pythonpath` in pyproject.toml (no product code changes):
  bridge (edge/bridge), regmap (simulators/vsite/maps), vsite (simulators/vsite), ingest, ems_cli (tools),
  csms (simulators/evse/csms), framework (tests/framework).
"""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from framework import RESULTS_DIR
from framework.artifacts import artifact_dir_for
from framework.clock import FakeClock
from framework.compose import ComposeStack
from framework.env import ENV_FILE, TestEnv, load_test_env
from framework.ids import TestIds, run_id
from framework.mqtt import Mqtt5Client

pytest_plugins = [
    "framework.plugins.levels",
    "framework.plugins.traceability",
    "framework.plugins.failure_artifacts",
    "pytester",  # fixture used by the framework's own plugin self-tests
]


def pytest_configure(config: pytest.Config) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_id()  # fix the run id before xdist workers start so they share it


# ---- environment ------------------------------------------------------------------------
@pytest.fixture(scope="session")
def results_dir() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


@pytest.fixture(scope="session")
def test_env(results_dir: Path) -> TestEnv:
    """Values from env > infra/.env > generated throw-away secrets. Redacted copy saved for debugging."""
    env = load_test_env()
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    (results_dir / f"env.redacted.{worker}.json").write_text(
        json.dumps({"source": env.source, "values": env.redacted()}, indent=1), encoding="utf-8"
    )
    return env


@pytest.fixture
def artifact_dir(request: pytest.FixtureRequest) -> Path:
    """test-results/artifacts/<nodeid>/ — put anything useful for diagnosing a failure here."""
    return artifact_dir_for(request.node.nodeid)


@pytest.fixture
def test_ids(request: pytest.FixtureRequest) -> TestIds:
    """Unique ids per test (data isolation on shared stacks/DBs)."""
    return TestIds(request.node.nodeid)


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


# ---- docker / emspoc stack (system tests) ----------------------------------------------
@pytest.fixture(scope="session")
def docker_available() -> bool:
    return ComposeStack.docker_available()


@pytest.fixture(scope="session")
def compose_stack(test_env: TestEnv, docker_available: bool) -> ComposeStack:
    """Attach to the running emspoc stack. Skips when it is not up.

    Starting it is allowed only with EMS_TEST_OWN_STACK=1 and EMS_TEST_STACK_UP=1 (CI system job /
    stack-owner agent); otherwise tests never change the stack's lifecycle.
    """
    if not docker_available:
        pytest.skip("Docker not reachable: system tests need the emspoc stack")
    stack = ComposeStack(project=test_env.compose_project, env_file=ENV_FILE)
    if not stack.is_up():
        if stack.owned and os.environ.get("EMS_TEST_STACK_UP") == "1":
            stack.up(build=True)
        else:
            pytest.skip(
                f"compose project {stack.project!r} is not up (start it: cd infra && docker compose up -d --wait)"
            )
    test_env.require_stack_credentials()
    return stack


@pytest.fixture
def mqtt_factory(test_env: TestEnv, test_ids: TestIds, artifact_dir: Path) -> Iterator[Callable[..., Mqtt5Client]]:
    """Create connected MQTT 5 clients: mqtt_factory("dispatcher") or mqtt_factory("ingest", host=..., port=...).

    Each client records a transcript to the test's artifact dir; all are closed at teardown.
    """
    clients: list[Mqtt5Client] = []

    def make(
        username: str | None,
        *,
        host: str | None = None,
        port: int | None = None,
        password: str | None = None,
        clean_start: bool = True,
    ) -> Mqtt5Client:
        pw = password if password is not None else (test_env.mqtt_credentials(username)[1] if username else None)
        cid = test_ids.client_id(username or "anon")
        client = Mqtt5Client(
            host=host or test_env.mqtt_host,
            port=port or test_env.mqtt_port,
            username=username,
            password=pw,
            client_id=cid,
            clean_start=clean_start,
            transcript_path=artifact_dir / f"mqtt-{cid}.jsonl",
        )
        client.connect()
        clients.append(client)
        return client

    yield make
    for c in clients:
        with contextlib.suppress(Exception):  # teardown best effort; the test result is what matters
            c.close()
