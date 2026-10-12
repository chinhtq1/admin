"""Self-tests of the traceability and policy plugins (pytester in a subprocess: isolation from xdist/cov)."""

from __future__ import annotations

import json
import os

import pytest

from framework import TESTS_ROOT

PLUGINS = (
    "-p",
    "framework.plugins.traceability",
    "-p",
    "framework.plugins.levels",
    "-p",
    "no:randomly",
    "-p",
    "no:cacheprovider",
)


@pytest.fixture
def results(tmp_path, monkeypatch):
    out = tmp_path / "results"
    monkeypatch.setenv("EMS_RESULTS_DIR", str(out))
    monkeypatch.setenv("PYTHONPATH", str(TESTS_ROOT))
    # the child pytest must not inherit xdist/pytest-cov worker state of the outer run
    for key in list(os.environ):
        if key.startswith(("COV_CORE_", "PYTEST_XDIST_", "COVERAGE_")) or key == "PYTEST_ADDOPTS":
            monkeypatch.delenv(key)
    return out


def test_traceability_report_maps_requirements_to_results(pytester, results):
    pytester.makepyfile(
        test_sample="""
        import pytest

        @pytest.mark.unit
        @pytest.mark.req("FR-INT-007", "NFR-SEC-011")
        def test_ok():
            pass

        @pytest.mark.unit
        @pytest.mark.req("FR-INT-007")
        @pytest.mark.bug("A1-BUG-01")
        @pytest.mark.xfail(strict=True, reason="A1-BUG-01 open")
        def test_known_bug():
            assert False

        @pytest.mark.unit
        def test_no_req():
            pass
    """
    )
    res = pytester.runpytest_subprocess(*PLUGINS)
    res.assert_outcomes(passed=2, xfailed=1)
    rep = json.loads((results / "traceability.json").read_text())
    assert rep["requirements"]["FR-INT-007"]["status"] == "PARTIAL"
    assert rep["requirements"]["NFR-SEC-011"]["status"] == "PASS"
    assert rep["requirements"]["FR-INT-007"]["in_scope"] is True
    assert rep["tests_without_req"] == ["test_sample.py::test_no_req"]
    assert rep["known_bug_tests"][0]["bugs"] == ["A1-BUG-01"]
    assert rep["scope"]["implemented_total"] == 52
    assert "FR-INT-007" in (results / "traceability.md").read_text()


def test_unknown_requirement_id_is_a_usage_error(pytester, results):
    pytester.makepyfile(
        test_bad="""
        import pytest

        @pytest.mark.unit
        @pytest.mark.req("FR-INT-999")
        def test_x():
            pass
    """
    )
    res = pytester.runpytest_subprocess(*PLUGINS)
    assert res.ret == pytest.ExitCode.USAGE_ERROR
    res.stderr.fnmatch_lines(["*FR-INT-999 not found*"])


def test_quarantine_requires_reason_and_issue(pytester, results):
    pytester.makepyfile(
        test_q="""
        import pytest

        @pytest.mark.unit
        @pytest.mark.quarantine(reason="timing on CI")
        def test_x():
            pass
    """
    )
    res = pytester.runpytest_subprocess(*PLUGINS)
    assert res.ret == pytest.ExitCode.USAGE_ERROR
    res.stderr.fnmatch_lines(["*quarantine needs reason*issue*"])


def test_quarantined_test_is_skipped_in_gating_runs(pytester, results):
    pytester.makepyfile(
        test_q="""
        import pytest

        @pytest.mark.unit
        @pytest.mark.quarantine(reason="timing on CI", issue="EMS-12")
        def test_x():
            assert False
    """
    )
    res = pytester.runpytest_subprocess(*PLUGINS)
    res.assert_outcomes(skipped=1)
    rep = json.loads((results / "traceability.json").read_text())
    assert rep["quarantined"][0]["issue"] == "EMS-12"


def test_blanket_reruns_are_forbidden(pytester, results, monkeypatch):
    monkeypatch.delenv("EMS_FLAKE_JOB", raising=False)
    pytester.makepyfile(test_r="def test_x():\n    pass\n")
    res = pytester.runpytest_subprocess(*PLUGINS, "--reruns", "2")
    assert res.ret == pytest.ExitCode.USAGE_ERROR
    res.stderr.fnmatch_lines(["*Blanket retries are forbidden*"])
