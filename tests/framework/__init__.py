"""EMS test framework helpers (shared by every test level).

Modules:
  env        test environment (infra/.env or generated, never secrets in the repo)
  wait       polling with explicit timeouts (no sleep-based asserts)
  clock      fake clock + per-module time/asyncio proxies
  ids        unique ids per test (data isolation), uuid7
  aio        run coroutines with an explicit timeout
  mqtt       MQTT 5 client wrapper (correlation data, ack waiting, transcript)
  envelopes  command envelope builder per 07 §8.3 (independent of tools/ems_cli.py)
  db         PostgreSQL helper (psycopg 3) + schema loader
  modbus     Modbus client helper decoding through a register map
  compose    docker compose stack manager (project emspoc), attach-only by default
  artifacts  per-test artifact directory under test-results/
  plugins/   pytest plugins: levels/timeouts, traceability, quarantine/flaky policy, failure artifacts
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = REPO_ROOT / "tests"
RESULTS_DIR = REPO_ROOT / "test-results"
