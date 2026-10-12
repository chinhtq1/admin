"""Test-level policy: level markers, default timeouts, quarantine and rerun rules.

- Every test gets exactly one *level* marker. Tests under tests/<level>/ get it automatically;
  tests under tests/system/ must declare `integration` or `e2e` explicitly.
- Default timeout per level (pytest-timeout) unless the test sets @pytest.mark.timeout.
- `@pytest.mark.quarantine(reason=..., issue=...)` is mandatory-argument; quarantined tests are skipped
  (visible in reports) unless --run-quarantined is given (flake-detection job).
- Blanket retries are forbidden: --reruns / @pytest.mark.flaky only in the flake-detection job
  (EMS_FLAKE_JOB=1). Gating jobs never retry.
"""

from __future__ import annotations

import os
import re

import pytest

LEVELS = ("unit", "property", "contract", "db", "integration", "e2e", "resilience", "security", "perf", "docs")

# tests/<dir>/... -> level applied automatically
DIR_LEVEL = {
    "unit": "unit",
    "property": "property",
    "contract": "contract",
    "db": "db",
    "resilience": "resilience",
    "security": "security",
    "perf": "perf",
    "docs": "docs",
}
SYSTEM_DIR = "system"  # integration/e2e must be explicit

# seconds; thread method for levels with background network threads (paho, docker)
LEVEL_TIMEOUT = {
    "unit": (30, "signal"),
    "property": (120, "signal"),
    "contract": (60, "signal"),
    "docs": (120, "thread"),
    "security": (300, "thread"),
    "db": (180, "thread"),
    "integration": (300, "thread"),
    "e2e": (900, "thread"),
    "resilience": (1200, "thread"),
    "perf": (1800, "thread"),
}

ISSUE_RE = re.compile(r"^(#\d+|[A-Z][A-Z0-9]+-\d+|https?://\S+)$")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ems", "EMS test framework")
    group.addoption(
        "--run-quarantined",
        action="store_true",
        default=False,
        help="run tests marked quarantine (flake-detection job only)",
    )


def _top_dir(item: pytest.Item) -> str | None:
    try:
        rel = item.path.relative_to(item.config.rootpath / "tests")
    except ValueError:
        return None
    return rel.parts[0] if len(rel.parts) > 1 else None


def pytest_configure(config: pytest.Config) -> None:
    flake_job = os.environ.get("EMS_FLAKE_JOB") == "1"
    reruns = getattr(config.option, "reruns", 0) or 0
    if reruns and not flake_job:
        raise pytest.UsageError(
            "Blanket retries are forbidden (--reruns). Use the flake-detection job (EMS_FLAKE_JOB=1) "
            "or fix/quarantine the test. See docs/testing/02-strategy.md, flaky policy."
        )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    errors: list[str] = []
    flake_job = os.environ.get("EMS_FLAKE_JOB") == "1"
    for item in items:
        top = _top_dir(item)
        if top in DIR_LEVEL:
            item.add_marker(getattr(pytest.mark, DIR_LEVEL[top]))
        levels = [lvl for lvl in LEVELS if item.get_closest_marker(lvl)]
        if top == "framework":
            pass  # never collected (no test files), defensive
        elif not levels:
            errors.append(f"{item.nodeid}: no level marker (one of {', '.join(LEVELS)})")
        elif top == SYSTEM_DIR and not ({"integration", "e2e"} & set(levels)):
            errors.append(f"{item.nodeid}: tests/system/ needs @pytest.mark.integration or @pytest.mark.e2e")

        # default timeout by the slowest level present
        if levels and not item.get_closest_marker("timeout"):
            secs, method = max(LEVEL_TIMEOUT[lvl] for lvl in levels)
            item.add_marker(pytest.mark.timeout(secs, method=method))

        # quarantine must carry reason + issue
        q = item.get_closest_marker("quarantine")
        if q is not None:
            reason, issue = q.kwargs.get("reason"), q.kwargs.get("issue")
            if not reason or not issue or not ISSUE_RE.match(str(issue)):
                errors.append(
                    f"{item.nodeid}: @pytest.mark.quarantine needs reason='...' and issue='#123'|'EMS-123'|URL"
                )
            elif not config.getoption("--run-quarantined"):
                item.add_marker(pytest.mark.skip(reason=f"QUARANTINED ({issue}): {reason}"))

        # no per-test retries outside the flake job
        if item.get_closest_marker("flaky") and not flake_job:
            errors.append(f"{item.nodeid}: @pytest.mark.flaky (retries) is forbidden; quarantine it instead")

        # known-bug link must come with strict xfail or a fix
        bug = item.get_closest_marker("bug")
        if bug is not None and not bug.args:
            errors.append(f"{item.nodeid}: @pytest.mark.bug needs an id, e.g. bug('A1-BUG-01')")

    if errors:
        raise pytest.UsageError("Test policy violations:\n  " + "\n  ".join(errors))
