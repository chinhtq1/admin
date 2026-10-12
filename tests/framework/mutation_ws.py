"""Build a mutmut workspace for core modules (used by `make mutation`).

Why: mutmut 3.8 derives module names from file paths relative to its cwd (or src/) and refuses to run
when tests import the code under another name. The product keeps several import roots
(edge/bridge -> `bridge`, simulators/vsite/maps -> `regmap`, ...), so we copy every import root into
<ws>/src/ (same module names as in the containers), copy tests + data files, and write a pyproject
with pythonpath ["tests", "src"]. No product file is modified.

    python tests/framework/mutation_ws.py --ws test-results/mutation --modules regmap aggregate
    cd test-results/mutation && ../../.venv/bin/mutmut run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# module key -> file inside the workspace src/ (import name preserved)
CORE = {
    "regmap": "regmap.py",
    "aggregate": "bridge/aggregate.py",
    "store": "bridge/store.py",
    "commands": "bridge/commands.py",
    "poller": "bridge/poller.py",
    "uplink": "bridge/uplink.py",
    "ingest": "ingest.py",
    "model": "vsite/model.py",
}
IMPORT_ROOTS = {  # repo path -> path under src/
    "edge/bridge/bridge": "bridge",
    "simulators/vsite/maps/regmap.py": "regmap.py",
    "simulators/vsite/vsite": "vsite",
    "ingest/ingest.py": "ingest.py",
    "tools/ems_cli.py": "ems_cli.py",
    "simulators/evse/csms/csms.py": "csms.py",
}
DATA = ["simulators/vsite/maps", "infra/config", "infra/db", "docs/research/ems/04-business-requirements.md"]
COMPONENT_TEST_DIRS = ("regmap", "bridge", "ingest", "vsite", "csms", "cli")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".hypothesis")


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, ignore=IGNORE, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def build(ws: Path, modules: list[str], tests: list[str]) -> None:
    unknown = [m for m in modules if m not in CORE]
    if unknown:
        raise SystemExit(f"unknown module(s) {unknown}; choose from {sorted(CORE)}")
    if ws.exists():
        shutil.rmtree(ws)
    for repo_path, src_path in IMPORT_ROOTS.items():
        _copy(ROOT / repo_path, ws / "src" / src_path)
    _copy(ROOT / "tests", ws / "tests")
    for d in DATA:
        _copy(ROOT / d, ws / d)
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    text = re.sub(r"pythonpath = \[[^\]]*\]", 'pythonpath = ["tests", "src"]', text, count=1)
    text = re.sub(r"source = \[[^\]]*\]", 'source = ["src"]', text, count=1)
    text = text.split("\n[tool.mutmut]")[0] + "\n"
    src_paths = ", ".join(f'"src/{CORE[m]}"' for m in modules)
    test_sel = ", ".join(f'"{t}"' for t in tests)
    text += (
        "[tool.mutmut]\n"
        f"source_paths = [{src_paths}]\n"
        f"pytest_add_cli_args_test_selection = [{test_sel}]\n"
        'pytest_add_cli_args = ["-p", "no:randomly", "-q", "-x"]\n'
        'also_copy = ["tests", "src", "simulators", "infra", "docs", "pyproject.toml"]\n'
    )
    (ws / "pyproject.toml").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ws", type=Path, default=ROOT / "test-results" / "mutation")
    ap.add_argument("--modules", nargs="+", default=["regmap", "aggregate", "store", "commands"])
    # product tests only: framework self-tests do not exercise product code
    ap.add_argument("--tests", nargs="+", default=[*(f"tests/unit/{c}" for c in COMPONENT_TEST_DIRS), "tests/property"])
    a = ap.parse_args(argv)
    build(a.ws, a.modules, a.tests)
    print(f"mutmut workspace: {a.ws} modules={a.modules} tests={a.tests}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
