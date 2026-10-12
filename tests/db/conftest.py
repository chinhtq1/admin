"""DB level: real TimescaleDB (same image as the PoC) in an ephemeral container, schema from infra/db/init.sql."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from framework.containers import timescaledb
from framework.db import Db
from framework.env import TestEnv


@pytest.fixture(scope="session")
def pg_dsn(test_env: TestEnv, docker_available: bool) -> Iterator[str]:
    if not docker_available:
        pytest.skip("Docker not reachable: db tests need an ephemeral TimescaleDB container")
    with timescaledb(test_env) as dsn:
        yield dsn


@pytest.fixture
def db(pg_dsn: str) -> Iterator[Db]:
    """Connection to the session DB. Isolate data with unique ids (test_ids), never TRUNCATE shared tables."""
    with Db(pg_dsn) as conn:
        yield conn
