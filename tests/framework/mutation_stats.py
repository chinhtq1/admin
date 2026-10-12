"""Convert mutants/mutmut-cicd-stats.json into test-results/mutation.json (used by framework.report).

Score = (killed + timeout) / (total - skipped - no_tests). Mutants without covering tests are reported
separately: they are a test-gap signal, not a score dilution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "test-results" / "mutation" / "mutants" / "mutmut-cicd-stats.json"
DST = ROOT / "test-results" / "mutation.json"


def main() -> int:
    if not SRC.is_file():
        print(f"no mutmut stats at {SRC} (mutmut run failed or produced nothing)")
        return 1
    s = json.loads(SRC.read_text(encoding="utf-8"))
    tested = int(s.get("total", 0)) - int(s.get("skipped", 0)) - int(s.get("no_tests", 0))
    killed = int(s.get("killed", 0)) + int(s.get("timeout", 0))
    if killed + int(s.get("survived", 0)) == 0:
        print(f"mutmut produced no results (see test-results/mutation/mutmut.log): {s}")
        return 1
    out = {**s, "tested": tested, "score_pct": round(100 * killed / tested, 1) if tested > 0 else None}
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
