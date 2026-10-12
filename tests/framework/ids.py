"""Unique identifiers for data isolation.

Tests that share a stack (emspoc) or a database must only read back data they created:
filter by a unique command_id / event marker / time window, never by "latest row".
"""

from __future__ import annotations

import itertools
import os
import re
import secrets
import time
import uuid
from dataclasses import dataclass, field

_counter = itertools.count(1)


def uuid7(ms: int | None = None) -> str:
    """RFC 9562 UUIDv7 (48-bit unix ms, version 7, variant 10). Independent of tools/ems_cli.py."""
    ms = int(time.time() * 1000) if ms is None else int(ms)
    rand = int.from_bytes(secrets.token_bytes(10), "big")
    value = (ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76
    value |= ((rand >> 62) & 0xFFF) << 64
    value |= 0b10 << 62
    value |= rand & ((1 << 62) - 1)
    return str(uuid.UUID(int=value))


def run_id() -> str:
    """One id per pytest session (stable across xdist workers if EMS_TEST_RUN_ID is exported)."""
    rid = os.environ.get("EMS_TEST_RUN_ID")
    if not rid:
        rid = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + "-" + secrets.token_hex(3)
        os.environ["EMS_TEST_RUN_ID"] = rid
    return rid


@dataclass
class TestIds:
    """Per-test id factory; `short` is safe for MQTT client ids, DB markers and file names."""

    __test__ = False

    nodeid: str
    run: str = field(default_factory=run_id)
    short: str = field(init=False)

    def __post_init__(self) -> None:
        worker = os.environ.get("PYTEST_XDIST_WORKER", "gw")
        self.short = f"t{self.run[-6:]}{worker[-2:]}{next(_counter):04d}"

    def uid(self, prefix: str = "") -> str:
        return f"{prefix}{self.short}-{secrets.token_hex(3)}"

    def command_id(self) -> str:
        return uuid7()

    def client_id(self, role: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "-", f"{role}-{self.uid()}")[:64]
