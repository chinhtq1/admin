# EMS automated tests — entry points. Docs: docs/testing/README.md, strategy: docs/testing/02-strategy.md
# All targets use the shared venv .venv (git-ignored). Results: test-results/ (git-ignored).

SHELL        := /bin/bash
.SHELLFLAGS  := -o pipefail -c
PYTHON       ?= python3
VENV         ?= .venv
PY           := $(VENV)/bin/python
PYTEST       := $(PY) -m pytest
RESULTS      := test-results
XDIST        ?= -n auto
# 1 = a level with no tests yet (pytest exit 5) is not a failure. CI sets 0 once the level is populated.
ALLOW_EMPTY  ?= 1
COV          := --cov --cov-append --cov-report=
COMPONENT_REQS := edge/bridge/requirements.txt ingest/requirements.txt simulators/vsite/requirements.txt \
                  simulators/evse/csms/requirements.txt tools/requirements.txt
# run_pytest(level, args...): junit + html per level; maps "no tests collected" (5) per ALLOW_EMPTY
define run_pytest
	@mkdir -p $(RESULTS); \
	$(PYTEST) $(2) --junitxml=$(RESULTS)/junit-$(1).xml --html=$(RESULTS)/report-$(1).html --self-contained-html; \
	rc=$$?; if [ $$rc -eq 5 ] && [ "$(ALLOW_EMPTY)" = "1" ]; then echo "[$(1)] no tests collected (ALLOW_EMPTY=1)"; rc=0; fi; exit $$rc
endef

.PHONY: help venv lint format test-unit test-property test-contract test-db test-integration test-e2e \
        test-resilience test-security test-perf test-docs test-smoke-legacy flake-detect mutation coverage \
        report gates ci-pr ci-main ci-nightly clean-results

help:
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-20s %s\n", $$1, $$2}'

venv: ## create .venv and install pinned test + component requirements
	test -x $(PY) || $(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements-test.txt $(addprefix -r ,$(COMPONENT_REQS))
	$(PY) -m pip check

lint: ## ruff on tests (gate) + product code (report only until owners adopt the config)
	$(VENV)/bin/ruff check tests
	$(VENV)/bin/ruff format --check tests
	-$(VENV)/bin/ruff check --exit-zero --statistics edge ingest simulators tools

format: ## auto-format test code
	$(VENV)/bin/ruff format tests
	$(VENV)/bin/ruff check --fix tests

test-unit: ## L1 unit tests (no I/O), parallel, coverage
	$(call run_pytest,unit,tests/unit -m unit $(XDIST) $(COV))

test-property: ## property-based tests (hypothesis)
	$(call run_pytest,property,tests/property -m property $(XDIST) $(COV))

test-contract: ## wire contracts: JSON Schema, MQTT 5 properties, golden vectors
	$(call run_pytest,contract,tests/contract -m contract $(XDIST) $(COV))

test-db: ## schema/SQL against ephemeral TimescaleDB (needs Docker)
	$(call run_pytest,db,tests/db -m db -p no:randomly $(COV))

test-integration: ## components + ephemeral Mosquitto/TimescaleDB (needs Docker)
	$(call run_pytest,integration,tests/system -m integration -p no:randomly $(COV))

test-e2e: ## attach to running emspoc stack (cd infra && docker compose up -d --wait)
	$(call run_pytest,e2e,tests/system -m e2e -p no:randomly)

test-resilience: ## fault injection on emspoc; stop/start needs EMS_TEST_OWN_STACK=1 (stack owner only)
	$(call run_pytest,resilience,tests/resilience -m resilience -p no:randomly)

test-security: ## security tests + bandit + pip-audit (+ gitleaks if installed)
	$(call run_pytest,security,tests/security -m security -p no:randomly)
	$(VENV)/bin/bandit -q -r edge ingest simulators tools -f json -o $(RESULTS)/bandit.json --severity-level medium || \
	  { echo "bandit findings: see $(RESULTS)/bandit.json"; exit 1; }
	for r in $(COMPONENT_REQS) requirements-test.txt; do $(VENV)/bin/pip-audit -r $$r --progress-spinner off || exit 1; done
	if command -v gitleaks >/dev/null; then gitleaks git . --redact --no-banner --report-path $(RESULTS)/gitleaks.json; \
	  else echo "gitleaks not installed: skipped (CI installs it)"; fi

test-perf: ## load/latency (nightly/release); attaches to emspoc
	$(call run_pytest,perf,tests/perf -m perf -p no:randomly)

test-docs: ## docs/wireframe checks (Playwright, PLAYWRIGHT_BROWSERS_PATH)
	$(call run_pytest,docs,tests/docs -m docs $(XDIST))

test-smoke-legacy: ## LEGACY bash smoke (superseded by tests/system e2e); needs running stack
	tests/smoke.sh

flake-detect: ## nightly: repeat suspect/quarantined tests; never used for gating
	EMS_FLAKE_JOB=1 $(PYTEST) tests/unit tests/property tests/contract --run-quarantined -p no:randomly \
	  --count $${FLAKE_COUNT:-20} $(XDIST) --junitxml=$(RESULTS)/junit-flake.xml || true
	$(PY) -m framework.report

mutation: ## mutmut on core modules (nightly); MUT_MODULES="regmap aggregate store commands"; -> test-results/mutation.json
	$(PY) tests/framework/mutation_ws.py --ws $(RESULTS)/mutation --modules $${MUT_MODULES:-regmap aggregate store commands}
	cd $(RESULTS)/mutation && ../../$(VENV)/bin/mutmut run --max-children $${MUT_CHILDREN:-4} >mutmut.log 2>&1; \
	  rc=$$?; grep -a -o 'mutations/second' mutmut.log >/dev/null || tail -20 mutmut.log; ../../$(VENV)/bin/mutmut export-cicd-stats >/dev/null; exit 0
	$(PY) tests/framework/mutation_stats.py

coverage: ## coverage report (line+branch) from all levels run so far
	$(VENV)/bin/coverage combine --keep >/dev/null 2>&1 || true
	$(VENV)/bin/coverage report
	$(VENV)/bin/coverage json -q
	$(VENV)/bin/coverage xml -q
	$(VENV)/bin/coverage html -q

report: ## traceability + metrics (test-results/traceability.md, metrics.md)
	-@$(MAKE) --no-print-directory coverage >/dev/null 2>&1
	cd tests && ../$(PY) -m framework.report --results ../$(RESULTS)

gates: ## evaluate offline-computable quality gates (exit 1 on failure)
	cd tests && ../$(PY) -m framework.report --results ../$(RESULTS) --check-gates

ci-pr: clean-results lint test-unit test-property test-contract test-docs report gates ## PR lane (< 10 min, no Docker)

ci-main: clean-results lint test-unit test-property test-contract test-docs test-db test-integration test-e2e test-security report gates ## main/merge lane

ci-nightly: ci-main test-resilience test-perf mutation flake-detect report ## nightly: + resilience, perf, mutation, flake hunt

clean-results: ## remove test-results/ (keeps nothing; traceability history restarts)
	rm -rf $(RESULTS) mutants .coverage .coverage.*
