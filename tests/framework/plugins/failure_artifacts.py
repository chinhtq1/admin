"""On failure of a system-level test, save diagnostics to test-results/artifacts/<nodeid>/.

- compose.log: `docker compose logs --since <test start>` of the emspoc project (read-only, allowed
  for everyone), only for markers integration/e2e/resilience/perf and only if Docker is reachable,
- report.txt: the failure representation.
MQTT transcripts are written by the mqtt fixture itself into the same directory.
Disable with EMS_NO_COMPOSE_LOGS=1.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

import pytest

from framework.artifacts import artifact_dir_for

SYSTEM_MARKERS = ("integration", "e2e", "resilience", "perf")
_START_KEY = pytest.StashKey[float]()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    item.stash[_START_KEY] = time.time()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    report = yield
    if report.when in ("setup", "call") and report.failed:
        try:
            _dump(item, report)
        except Exception as exc:  # artifact collection must never mask the real failure
            report.sections.append(("ems artifacts", f"artifact collection failed: {exc!r}"))
    return report


def _dump(item: pytest.Item, report: pytest.TestReport) -> None:
    out = artifact_dir_for(item.nodeid)
    (out / "report.txt").write_text(str(report.longrepr), encoding="utf-8")
    if not any(item.get_closest_marker(m) for m in SYSTEM_MARKERS) or os.environ.get("EMS_NO_COMPOSE_LOGS") == "1":
        return
    from framework.compose import ComposeStack  # local import: unit runs never touch docker
    from framework.env import load_test_env

    if not ComposeStack.docker_available():
        return
    env = load_test_env()
    stack = ComposeStack(project=env.compose_project)
    started = item.stash.get(_START_KEY, time.time() - 600) - 5
    since = datetime.fromtimestamp(started, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    (out / "compose.log").write_text(stack.logs(since=since, tail=None), encoding="utf-8")
    (out / "compose-ps.txt").write_text(repr(stack.service_states()), encoding="utf-8")
    report.sections.append(("ems artifacts", f"saved to {out}"))
