"""Command envelope builder per 07 §8.3 (ems.command.v1), independent of tools/ems_cli.py.

Kept independent on purpose: system tests act as the cloud dispatcher and must keep working when
tools/ems_cli.py is replaced by the Java Command API. Field set mirrors 07 §8.3 as implemented in
the PoC (signature is "UNSIGNED-POC" until JWS/ADR-13 exists).
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

from framework.ids import uuid7


def iso_ms(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def command_envelope(
    *,
    edge_id: str,
    ctype: str,
    params: dict[str, Any],
    asset_id: str,
    site_id: str = "site-bd-01",
    duration_s: float = 600,
    now: datetime | None = None,
    valid_from: datetime | None = None,
    expires_at: datetime | None = None,
    seq: int | None = None,
    danger_class: str = "C1",
    reason: str | None = None,
    max_latency_ms: int = 10_000,
    readback_timeout_s: float = 10,
    abs_w: float = 1,
    kid: str = "test-dispatcher",
    command_id: str | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    now = now or datetime.now(UTC)
    valid_from = valid_from or now
    expires_at = expires_at or (valid_from + timedelta(seconds=duration_s))
    env: dict[str, Any] = {
        "schema": "ems.command.v1",
        "command_id": command_id or uuid7(),
        "seq": int(time.time() * 1000) if seq is None else seq,
        "type": ctype,
        "target": {"edge_id": edge_id, "site_id": site_id, "asset_id": asset_id},
        "params": params,
        "source": "OPERATOR",
        "danger_class": danger_class,
        "issued_by": "user:automated-test",
        "valid_from": iso_ms(valid_from),
        "expires_at": iso_ms(expires_at),
        "sent_at": iso_ms(now),
        "max_latency_ms": max_latency_ms,
        "on_expiry": "REVERT_DEFAULT",
        "tolerance": {"abs_w": abs_w, "readback_timeout_s": readback_timeout_s},
        "dry_run": False,
        "kid": kid,
        "signature": "UNSIGNED-POC",
    }
    if reason:
        env["reason"] = reason
    env.update(overrides)
    return env


def message_expiry_s(env: dict[str, Any]) -> int | None:
    """MQTT Message Expiry = expires_at - sent_at, rounded down (07 §8.2a); None if already expired."""
    exp = datetime.fromisoformat(env["expires_at"].replace("Z", "+00:00"))
    sent = datetime.fromisoformat(env["sent_at"].replace("Z", "+00:00"))
    secs = int((exp - sent).total_seconds())
    return secs if secs > 0 else None
