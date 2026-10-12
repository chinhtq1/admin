"""Ephemeral infrastructure for db/integration tests (testcontainers; NOT the emspoc stack).

Images are the same tags as infra/docker-compose.yml so behaviour matches the PoC. Containers get
random host ports and are removed by Ryuk; credentials are generated per session (framework.env).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from framework import REPO_ROOT
from framework.env import MQTT_USERS, TestEnv

MOSQUITTO_IMAGE = "eclipse-mosquitto:2.0.20"
TIMESCALE_IMAGE = "timescale/timescaledb:2.17.2-pg16"
MOSQUITTO_DIR = REPO_ROOT / "infra" / "mosquitto"


@dataclass(frozen=True)
class Endpoint:
    host: str
    port: int


@contextmanager
def timescaledb(env: TestEnv, *, apply_init_sql: bool = True, startup_timeout: int = 120) -> Iterator[str]:
    """Start TimescaleDB like the PoC (license=apache); yield a libpq DSN. Applies infra/db/init.sql."""
    from testcontainers.community.postgres import PostgresContainer

    pg = PostgresContainer(
        TIMESCALE_IMAGE, username="ems", password=env.secret("DB_PASSWORD"), dbname="ems", driver=None
    )
    pg.with_command("postgres -c timescaledb.license=apache -c timescaledb.telemetry_level=off")
    with pg:
        host, port = pg.get_container_host_ip(), pg.get_exposed_port(5432)
        dsn = f"host={host} port={port} dbname=ems user=ems password={env.secret('DB_PASSWORD')}"
        if apply_init_sql:
            from framework.db import Db

            with Db(dsn, connect_timeout=10) as db:
                db.apply_sql_file()
        yield dsn


@contextmanager
def mosquitto(env: TestEnv, *, startup_timeout: int = 60) -> Iterator[Endpoint]:
    """Start Mosquitto with the PoC's mosquitto.conf, acl.conf and entrypoint (password file from env)."""
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.wait_strategies import LogMessageWaitStrategy

    c = (
        DockerContainer(MOSQUITTO_IMAGE)
        .with_exposed_ports(1883)
        .with_volume_mapping(str(MOSQUITTO_DIR / "mosquitto.conf"), "/mosquitto/config/mosquitto.conf", "ro")
        .with_volume_mapping(str(MOSQUITTO_DIR / "acl.conf"), "/mosquitto/config/acl.conf", "ro")
        .with_volume_mapping(str(MOSQUITTO_DIR / "entrypoint.sh"), "/mosquitto/config/entrypoint.sh", "ro")
        .with_kwargs(entrypoint=["/bin/sh", "/mosquitto/config/entrypoint.sh"])
    )
    for _user, key in MQTT_USERS.items():
        c.with_env(key, env.secret(key))
    c.waiting_for(
        LogMessageWaitStrategy(re.compile(r"mosquitto version .* running")).with_startup_timeout(startup_timeout)
    )
    with c:
        yield Endpoint(c.get_container_host_ip(), int(c.get_exposed_port(1883)))
