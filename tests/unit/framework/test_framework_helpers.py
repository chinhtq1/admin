"""Self-tests of the framework helpers (no product requirement)."""

from __future__ import annotations

import time
import uuid

import pytest

from framework.clock import FakeClock, patch_module_time
from framework.env import SECRET_KEYS, load_test_env, parse_env_file
from framework.envelopes import command_envelope, message_expiry_s
from framework.ids import TestIds, uuid7
from framework.wait import WaitTimeout, wait_for_value, wait_until


def test_wait_until_returns_first_truthy_value():
    calls = iter([0, 0, 7])
    assert wait_until(lambda: next(calls), timeout=2, interval=0.001) == 7


def test_wait_timeout_reports_last_value():
    with pytest.raises(WaitTimeout, match=r"last value: 'nope'"):
        wait_for_value(lambda: "nope", lambda v: v == "yes", timeout=0.05, interval=0.01, desc="yes")


def test_fake_clock_wall_step_does_not_move_monotonic():
    c = FakeClock(wall_ms=10_000, monotonic_s=5.0)
    c.advance(1.5)
    c.step_wall(-3)
    assert c.now_ms() == 8_500
    assert c.monotonic() == pytest.approx(6.5)
    with pytest.raises(ValueError, match="only moves forward"):
        c.advance(-1)


def test_patch_module_time_is_local_to_module(monkeypatch):
    import types

    mod = types.ModuleType("fake_product_module")
    mod.time = time
    clock = FakeClock(wall_ms=1_000)
    patch_module_time(monkeypatch, mod, clock)
    assert mod.time.time() == 1.0
    assert time.time() > 1_700_000_000  # global time untouched
    assert mod.time.sleep is time.sleep  # everything else delegates


def test_uuid7_version_variant_and_order():
    a, b = uuid7(ms=1_000), uuid7(ms=2_000)
    ua = uuid.UUID(a)
    assert ua.version == 7
    assert ua.variant == uuid.RFC_4122
    assert a < b


def test_test_ids_are_unique():
    ids = TestIds("tests/x.py::t")
    assert len({ids.uid() for _ in range(100)}) == 100
    assert len(ids.client_id("dispatcher")) <= 64


def test_env_file_parsing_and_generated_secrets(tmp_path):
    f = tmp_path / ".env"
    f.write_text("# c\nDB_PASSWORD='from-file'\nexport SIM_SPEED=1\n\n", encoding="utf-8")
    assert parse_env_file(f) == {"DB_PASSWORD": "from-file", "SIM_SPEED": "1"}
    env = load_test_env(environ={"MQTT_PASS_INGEST": "from-env"}, env_file=f)
    assert env.secret("DB_PASSWORD") == "from-file"
    assert env.secret("MQTT_PASS_INGEST") == "from-env"
    assert "MQTT_PASS_DISPATCHER" in env.generated
    red = env.redacted()
    assert all(red[k] in ("<set>", "<generated>") for k in SECRET_KEYS)
    with pytest.raises(RuntimeError, match="real credentials"):
        env.require_stack_credentials()


def test_command_envelope_expiry():
    env = command_envelope(
        edge_id="edge-vsite01", ctype="SET_ESS_P", params={"p_w": 0}, asset_id="ess-01", duration_s=120
    )
    assert message_expiry_s(env) == 120
    assert env["target"] == {"edge_id": "edge-vsite01", "site_id": "site-bd-01", "asset_id": "ess-01"}
