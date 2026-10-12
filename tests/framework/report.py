"""Quality metrics summary: `python -m framework.report [--check-gates]` (run by `make report`).

Inputs (all optional, from test-results/):
  traceability-db.json   last result per test (written by the traceability plugin)
  junit-*.xml            durations per level run
  coverage.json          `coverage json` output (line + branch)
  quality-baseline.json  in tests/ — committed ratchet baseline (core branch coverage, mutation score)
  mutation.json          written by `make mutation` (killed/survived counts)
Outputs: test-results/metrics.json, test-results/metrics.md
Gate check (--check-gates) exits 1 when a gate in docs/testing/02-strategy.md §6 that is computable
offline fails: failed/error tests, xpassed known bugs, tests without level (enforced at collection),
core branch-coverage ratchet, quarantine budget.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET  # noqa: S405 - parsing our own junit files
from pathlib import Path
from typing import Any

from framework import RESULTS_DIR, TESTS_ROOT
from framework.plugins.traceability import _is_flaky, build_report, load_scope

CORE_MODULES = [
    "edge/bridge/bridge/commands.py",
    "edge/bridge/bridge/store.py",
    "edge/bridge/bridge/aggregate.py",
    "edge/bridge/bridge/poller.py",
    "edge/bridge/bridge/uplink.py",
    "ingest/ingest.py",
    "simulators/vsite/maps/regmap.py",
    "simulators/vsite/vsite/model.py",
]
BASELINE_FILE = TESTS_ROOT / "quality-baseline.json"
RATCHET_TOLERANCE_PP = 0.5
QUARANTINE_BUDGET = 5


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except ValueError:
        return None


def junit_durations(results: Path) -> dict[str, dict[str, float]]:
    out = {}
    for f in sorted(results.glob("junit-*.xml")):
        try:
            root = ET.parse(f).getroot()  # noqa: S314
        except ET.ParseError:
            continue
        suites = [root] if root.tag == "testsuite" else list(root)
        out[f.stem.removeprefix("junit-")] = {
            "tests": sum(int(s.get("tests", 0)) for s in suites),
            "failures": sum(int(s.get("failures", 0)) for s in suites),
            "errors": sum(int(s.get("errors", 0)) for s in suites),
            "skipped": sum(int(s.get("skipped", 0)) for s in suites),
            "time_s": round(sum(float(s.get("time", 0)) for s in suites), 2),
        }
    return out


def core_coverage(cov: dict[str, Any] | None) -> dict[str, Any] | None:
    if not cov:
        return None
    files = cov.get("files", {})
    per, stmts, cov_l, br, cov_b = {}, 0, 0, 0, 0
    for mod in CORE_MODULES:
        s = files.get(mod, {}).get("summary")
        if not s:
            per[mod] = None
            continue
        per[mod] = {
            "line_pct": round(100 * s["covered_lines"] / s["num_statements"], 1) if s["num_statements"] else None,
            "branch_pct": round(100 * s.get("covered_branches", 0) / s["num_branches"], 1)
            if s.get("num_branches")
            else None,
        }
        stmts += s["num_statements"]
        cov_l += s["covered_lines"]
        br += s.get("num_branches", 0)
        cov_b += s.get("covered_branches", 0)
    return {
        "modules": per,
        "line_pct": round(100 * cov_l / stmts, 1) if stmts else 0.0,
        "branch_pct": round(100 * cov_b / br, 1) if br else 0.0,
    }


def compute(results: Path = RESULTS_DIR) -> dict[str, Any]:
    db = _load(results / "traceability-db.json") or {"tests": {}}
    trace = build_report(db, load_scope())
    tests = db.get("tests", {})
    histories = [t.get("history", []) for t in tests.values()]
    runs = sum(1 for h in histories for e in h if not e[2].startswith("rerun"))
    fails = sum(1 for h in histories for e in h if e[2] in ("failed", "error"))
    flaky = sum(1 for h in histories if _is_flaky(h))
    return {
        "summary": trace["summary"],
        "req_coverage_implemented_scope": trace["scope"],
        "rates": {
            "executions_in_history": runs,
            "fail_rate_pct": round(100 * fails / runs, 2) if runs else None,
            "flaky_tests": flaky,
            "flaky_rate_pct": round(100 * flaky / len(tests), 2) if tests else None,
        },
        "levels": junit_durations(results),
        "core_coverage": core_coverage(_load(results / "coverage.json")),
        "mutation": _load(results / "mutation.json"),
        "known_bug_tests": trace["known_bug_tests"],
        "quarantined": trace["quarantined"],
        "baseline": _load(BASELINE_FILE),
    }


def check_gates(m: dict[str, Any]) -> list[str]:
    failures = []
    s = m["summary"]
    if s.get("failed", 0) or s.get("error", 0):
        failures.append(f"G1 failed/error tests: failed={s.get('failed', 0)} error={s.get('error', 0)}")
    if s.get("xpassed", 0):
        failures.append(f"G2 xpassed known-bug tests: {s['xpassed']} (bug fixed? remove xfail and close the bug)")
    if len(m["quarantined"]) > QUARANTINE_BUDGET:
        failures.append(f"G5 quarantine budget exceeded: {len(m['quarantined'])} > {QUARANTINE_BUDGET}")
    base = (m.get("baseline") or {}).get("core_branch_pct")
    cur = (m.get("core_coverage") or {}).get("branch_pct")
    if base is not None and cur is not None and cur < base - RATCHET_TOLERANCE_PP:
        failures.append(f"G4 core branch coverage ratchet: {cur}% < baseline {base}% - {RATCHET_TOLERANCE_PP}pp")
    return failures


def render(m: dict[str, Any]) -> str:
    s, sc, r = m["summary"], m["req_coverage_implemented_scope"], m["rates"]
    lines = [
        "# Test metrics (generated)",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Tests (last result) | {s['tests']} — " + ", ".join(f"{k} {v}" for k, v in s.items() if k != "tests") + " |",
        f"| Req coverage, implemented scope | {sc['covered']}/{sc['implemented_total']} ({sc['covered_pct']}%), "
        f"passing {sc['passing']} ({sc['passing_pct']}%) |",
        f"| Fail rate (history) | {r['fail_rate_pct']}% of {r['executions_in_history']} executions |",
        f"| Flaky tests (pass+fail on same commit) | {r['flaky_tests']} ({r['flaky_rate_pct']}%) |",
    ]
    cc = m.get("core_coverage")
    if cc:
        lines.append(f"| Core coverage (line / branch) | {cc['line_pct']}% / {cc['branch_pct']}% |")
    mu = m.get("mutation")
    if mu:
        lines.append(f"| Mutation score (core) | {mu.get('score_pct')}% ({mu.get('killed')}/{mu.get('total')}) |")
    for lvl, d in m["levels"].items():
        lines.append(
            f"| Level `{lvl}` | {d['tests']} tests, {d['failures']} failed, {d['errors']} errors, "
            f"{d['skipped']} skipped, {d['time_s']} s |"
        )
    if cc:
        lines += ["", "## Core modules", "", "| Module | Line % | Branch % |", "|---|---|---|"]
        for mod, v in cc["modules"].items():
            lines.append(f"| `{mod}` | {v['line_pct'] if v else '-'} | {v['branch_pct'] if v else '-'} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", type=Path, default=RESULTS_DIR)
    ap.add_argument("--check-gates", action="store_true")
    a = ap.parse_args(argv)
    m = compute(a.results)
    a.results.mkdir(parents=True, exist_ok=True)
    (a.results / "metrics.json").write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    (a.results / "metrics.md").write_text(render(m), encoding="utf-8")
    print(render(m))
    if a.check_gates:
        fails = check_gates(m)
        for f in fails:
            print("GATE FAIL:", f)
        return 1 if fails else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
