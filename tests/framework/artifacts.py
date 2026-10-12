"""Per-test artifact directories under test-results/artifacts/<sanitized nodeid>/."""

from __future__ import annotations

import re
from pathlib import Path

from framework import RESULTS_DIR

ARTIFACTS_DIR = RESULTS_DIR / "artifacts"


def sanitize_nodeid(nodeid: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid.replace("::", "__"))
    return s.strip("_")[:180]


def artifact_dir_for(nodeid: str, create: bool = True) -> Path:
    d = ARTIFACTS_DIR / sanitize_nodeid(nodeid)
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d
