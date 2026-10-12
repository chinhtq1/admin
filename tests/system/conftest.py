"""System level (tests/system): integration (ephemeral containers) and e2e (attach to emspoc stack)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from framework.compose import ComposeStack
from framework.containers import Endpoint, mosquitto
from framework.db import Db
from framework.env import TestEnv


@pytest.fixture(scope="session")
def mqtt_broker(test_env: TestEnv, docker_available: bool) -> Iterator[Endpoint]:
    """Ephemeral Mosquitto 2.0.20 with the PoC's conf/ACL (integration tests; generated passwords)."""
    if not docker_available:
        pytest.skip("Docker not reachable: integration tests need an ephemeral Mosquitto container")
    with mosquitto(test_env) as ep:
        yield ep


@pytest.fixture
def stack_db(compose_stack: ComposeStack, test_env: TestEnv) -> Iterator[Db]:
    """DB of the running emspoc stack (e2e). Read only rows your test created (filter by test ids/time)."""
    with Db(test_env.db_dsn()) as conn:
        yield conn
