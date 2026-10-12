"""Requirement traceability: @pytest.mark.req("FR-INT-007", "NFR-SEC-011", ...).

Collection
- validates ids against the catalog parsed from docs/research/ems/04-business-requirements.md
  (unknown id -> usage error; typo-proof), stores them in item.user_properties (survives xdist).
Reporting (controller process only)
- keeps a per-test result store test-results/traceability-db.json (last result + short history per
  nodeid, keyed by git commit) so separate level runs (unit, contract, ...) merge into one view,
- writes test-results/traceability.json and test-results/traceability.md: requirement -> tests ->
  last result, coverage over the implemented scope (tests/framework/data/implemented_scope.txt),
  tests without requirement, quarantined tests, known-bug tests and flaky candidates
  (same commit, both pass and fail).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

from framework import REPO_ROOT, RESULTS_DIR

REQ_RE = re.compile(r"^(FR|NFR)-[A-Z]+-\d{3}$")
CATALOG_DOC = REPO_ROOT / "docs" / "research" / "ems" / "04-business-requirements.md"
SCOPE_FILE = Path(__file__).resolve().parents[1] / "data" / "implemented_scope.txt"
DB_FILE = "traceability-db.json"
HISTORY_MAX = 30
# Self-tests of the framework verify no product requirement; they are not reported as "without req".
FRAMEWORK_SELFTEST_PREFIX = "tests/unit/framework/"
LEVELS = ("unit", "property", "contract", "db", "integration", "e2e", "resilience", "security", "perf", "docs")


def load_catalog(path: Path = CATALOG_DOC) -> set[str]:
    if not path.is_file():
        return set()
    return set(re.findall(r"\b(?:FR|NFR)-[A-Z]+-\d{3}\b", path.read_text(encoding="utf-8")))


def load_scope(path: Path = SCOPE_FILE) -> list[str]:
    if not path.is_file():
        return []
    ids = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        rid = raw.split("#", 1)[0].strip()
        if rid:
            ids.append(rid)
    return ids


def _git_commit() -> str:
    env_commit = os.environ.get("GITHUB_SHA") or os.environ.get("EMS_GIT_COMMIT")
    if env_commit:
        return env_commit[:12]
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        commit = out.stdout.strip() or "unknown"
        return commit + ("+dirty" if dirty.stdout.strip() else "")
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


_REPEAT_SUFFIX = re.compile(r"(?:\[|-)\d+-\d+\]$")


def base_nodeid(nodeid: str, repeating: bool) -> str:
    """Strip pytest-repeat's '[i-n]' / '-i-n]' suffix so repeated runs aggregate on one test."""
    if not repeating:
        return nodeid
    m = _REPEAT_SUFFIX.search(nodeid)
    if not m:
        return nodeid
    head = nodeid[: m.start()]
    return head + ("]" if m.group(0).startswith("-") else "")


class TraceabilityPlugin:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.catalog = load_catalog()
        self.scope = load_scope()
        self.results: dict[str, dict[str, Any]] = {}
        self.meta: dict[str, dict[str, Any]] = {}
        self.started = time.time()
        self.repeating = (getattr(config.option, "count", 1) or 1) > 1

    # ---- collection (runs in every process) ------------------------------------------
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        errors = []
        for item in items:
            reqs: list[str] = []
            for mark in item.iter_markers("req"):
                for rid in mark.args:
                    if not isinstance(rid, str) or not REQ_RE.match(rid):
                        errors.append(
                            f"{item.nodeid}: invalid requirement id {rid!r} (expected FR-XXX-NNN / NFR-XXX-NNN)"
                        )
                    elif self.catalog and rid not in self.catalog:
                        errors.append(f"{item.nodeid}: {rid} not found in {CATALOG_DOC.relative_to(REPO_ROOT)}")
                    else:
                        reqs.append(rid)
            levels = [lvl for lvl in LEVELS if item.get_closest_marker(lvl)]
            bugs = [str(a) for m in item.iter_markers("bug") for a in m.args]
            q = item.get_closest_marker("quarantine")
            item.user_properties.append(
                (
                    "ems_trace",
                    json.dumps(
                        {
                            "reqs": sorted(set(reqs)),
                            "levels": levels,
                            "bugs": bugs,
                            "quarantine": dict(q.kwargs) if q else None,
                        }
                    ),
                )
            )
        if errors:
            raise pytest.UsageError("Traceability errors:\n  " + "\n  ".join(errors))

    # ---- results (controller) -----------------------------------------------------------
    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        nodeid = report.nodeid
        for key, value in report.user_properties:
            if key == "ems_trace" and nodeid not in self.meta:
                self.meta[nodeid] = json.loads(value)
        r = self.results.setdefault(nodeid, {"outcome": None, "duration": 0.0, "reruns": 0})
        r["duration"] += float(getattr(report, "duration", 0.0) or 0.0)
        if report.outcome == "rerun":
            r["reruns"] += 1
            return
        if report.when == "setup":
            if report.failed:
                r["outcome"] = "error"
            elif report.skipped:
                r["outcome"] = "xfailed" if hasattr(report, "wasxfail") else "skipped"
        elif report.when == "call":
            if hasattr(report, "wasxfail"):
                r["outcome"] = "xfailed" if report.skipped else "xpassed"
            else:
                r["outcome"] = report.outcome
        elif report.when == "teardown" and report.failed and r["outcome"] in (None, "passed"):
            r["outcome"] = "error"

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if hasattr(self.config, "workerinput"):  # xdist worker: controller writes
            return
        if not self.results:
            return
        out_dir = Path(os.environ.get("EMS_RESULTS_DIR", str(RESULTS_DIR)))
        out_dir.mkdir(parents=True, exist_ok=True)
        db = self._update_db(out_dir / DB_FILE)
        report = build_report(db, self.scope)
        (out_dir / "traceability.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (out_dir / "traceability.md").write_text(render_markdown(report), encoding="utf-8")

    def _update_db(self, path: Path) -> dict[str, Any]:
        try:
            db = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        except ValueError:
            db = {}
        tests = db.setdefault("tests", {})
        commit = _git_commit()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = os.environ.get("EMS_TEST_RUN_ID", now)
        agg: dict[str, dict[str, Any]] = {}
        for nodeid, r in self.results.items():
            if r["outcome"] is None:
                continue
            base = base_nodeid(nodeid, self.repeating)
            a = agg.setdefault(base, {"outcomes": [], "duration": 0.0, "reruns": 0, "meta": self.meta.get(nodeid, {})})
            a["outcomes"].append(r["outcome"])
            a["duration"] += r["duration"]
            a["reruns"] += r["reruns"]
        for base, a in agg.items():
            entry = tests.setdefault(base, {"history": []})
            meta = a["meta"]
            outcomes = a["outcomes"]
            last = "failed" if "failed" in outcomes else ("error" if "error" in outcomes else outcomes[-1])
            entry.update(
                {
                    "reqs": meta.get("reqs", []),
                    "levels": meta.get("levels", []),
                    "bugs": meta.get("bugs", []),
                    "quarantine": meta.get("quarantine"),
                    "last_outcome": last,
                    "last_run": now,
                    "last_commit": commit,
                    "last_duration_s": round(a["duration"], 4),
                    "run_id": run_id,
                }
            )
            for o in outcomes:
                entry["history"].append([now, commit, o])
            if a["reruns"]:
                entry["history"].append([now, commit, f"rerun x{a['reruns']}"])
            entry["history"] = entry["history"][-HISTORY_MAX:]
        db["updated"] = now
        path.write_text(json.dumps(db, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return db


def _is_flaky(history: list[list[str]]) -> bool:
    by_commit: dict[str, set[str]] = defaultdict(set)
    for _ts, commit, outcome in history:
        if outcome.startswith("rerun"):
            by_commit[commit].add("failed")
        else:
            by_commit[commit].add(outcome)
    return any({"passed", "failed"} <= s or {"passed", "error"} <= s for s in by_commit.values())


def build_report(db: dict[str, Any], scope: list[str]) -> dict[str, Any]:
    tests = db.get("tests", {})
    reqs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    without, quarantined, bugs, flaky, selftests = [], [], [], [], 0
    counts: dict[str, int] = defaultdict(int)
    for nodeid, t in sorted(tests.items()):
        counts[t["last_outcome"]] += 1
        row = {
            "nodeid": nodeid,
            "outcome": t["last_outcome"],
            "levels": t.get("levels", []),
            "last_run": t.get("last_run"),
            "commit": t.get("last_commit"),
            "bugs": t.get("bugs", []),
        }
        if nodeid.startswith(FRAMEWORK_SELFTEST_PREFIX):
            selftests += 1
        elif not t.get("reqs"):
            without.append(nodeid)
        for rid in t.get("reqs", []):
            reqs[rid].append(row)
        if t.get("quarantine"):
            quarantined.append({"nodeid": nodeid, **t["quarantine"]})
        if t.get("bugs"):
            bugs.append({"nodeid": nodeid, "bugs": t["bugs"], "outcome": t["last_outcome"]})
        if _is_flaky(t.get("history", [])):
            flaky.append(nodeid)

    def req_status(rows: list[dict[str, Any]]) -> str:
        outs = {r["outcome"] for r in rows}
        if outs & {"failed", "error", "xpassed"}:
            return "FAIL"
        if "passed" in outs:
            return "PASS" if outs <= {"passed", "skipped"} else "PARTIAL"  # xfailed = known bug open
        if "xfailed" in outs:
            return "KNOWN_BUG"
        return "NOT_RUN"

    requirements = {
        rid: {"status": req_status(rows), "in_scope": rid in scope, "tests": rows} for rid, rows in sorted(reqs.items())
    }
    covered = [r for r in scope if r in requirements]
    passing = [r for r in scope if requirements.get(r, {}).get("status") == "PASS"]
    total = sum(counts.values())
    return {
        "generated": db.get("updated"),
        "summary": {
            "tests": total,
            **dict(sorted(counts.items())),
            "framework_selftests": selftests,
            "with_req": total - len(without) - selftests,
            "without_req": len(without),
            "quarantined": len(quarantined),
            "flaky_candidates": len(flaky),
        },
        "scope": {
            "implemented_total": len(scope),
            "covered": len(covered),
            "passing": len(passing),
            "covered_pct": round(100 * len(covered) / len(scope), 1) if scope else None,
            "passing_pct": round(100 * len(passing) / len(scope), 1) if scope else None,
            "uncovered": [r for r in scope if r not in requirements],
        },
        "requirements": requirements,
        "out_of_scope_reqs": sorted(r for r in requirements if r not in scope),
        "tests_without_req": without,
        "quarantined": quarantined,
        "known_bug_tests": bugs,
        "flaky_candidates": flaky,
    }


def render_markdown(rep: dict[str, Any]) -> str:
    s, sc = rep["summary"], rep["scope"]
    lines = [
        "# Traceability report (generated — do not edit)",
        "",
        f"- Generated: {rep['generated']} · Source: `test-results/traceability-db.json` (last result per test)",
        f"- Tests: {s['tests']} · " + " · ".join(f"{k}: {v}" for k, v in s.items() if k != "tests"),
        f"- Implemented-scope coverage: {sc['covered']}/{sc['implemented_total']} requirements have >= 1 test "
        f"({sc['covered_pct']}%), {sc['passing']} fully passing ({sc['passing_pct']}%)",
        "",
        "| Requirement | In scope | Status | Tests (last result) |",
        "|---|---|---|---|",
    ]
    for rid, r in rep["requirements"].items():
        tests = "<br>".join(
            f"`{t['nodeid']}` — {t['outcome']}" + (f" ({', '.join(t['bugs'])})" if t["bugs"] else "")
            for t in r["tests"]
        )
        lines.append(f"| {rid} | {'yes' if r['in_scope'] else 'no'} | {r['status']} | {tests} |")
    lines += [
        "",
        f"## Uncovered implemented-scope requirements ({len(sc['uncovered'])})",
        "",
        ", ".join(sc["uncovered"]) or "none",
        "",
        f"## Tests without requirement ({len(rep['tests_without_req'])})",
        "",
    ]
    lines += [f"- `{n}`" for n in rep["tests_without_req"]] or ["none"]
    lines += ["", f"## Quarantined ({len(rep['quarantined'])})", ""]
    lines += [f"- `{q['nodeid']}` — {q.get('issue')}: {q.get('reason')}" for q in rep["quarantined"]] or ["none"]
    lines += ["", f"## Known-bug tests ({len(rep['known_bug_tests'])})", ""]
    lines += [f"- `{b['nodeid']}` — {', '.join(b['bugs'])} — {b['outcome']}" for b in rep["known_bug_tests"]] or [
        "none"
    ]
    lines += ["", f"## Flaky candidates ({len(rep['flaky_candidates'])})", ""]
    lines += [f"- `{n}`" for n in rep["flaky_candidates"]] or ["none"]
    return "\n".join(lines) + "\n"


def pytest_configure(config: pytest.Config) -> None:
    if not config.pluginmanager.has_plugin("ems-traceability"):
        config.pluginmanager.register(TraceabilityPlugin(config), "ems-traceability")
