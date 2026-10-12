"""Example unit test (framework reference): register codec golden vectors with an INDEPENDENT oracle.

Expected words are computed by hand from the two's-complement definition, not by calling the codec
(R-15-01: vsite and bridge share regmap.py, so round-trip tests alone cannot catch symmetric bugs).
Owner of the full regmap suite may extend/replace this file; keep the req tags.
"""

from __future__ import annotations

import pytest

from framework.modbus import load_register_map


@pytest.fixture(scope="module")
def bess_map():
    return load_register_map("generic_bess_pcs.yaml")


@pytest.mark.req("FR-INT-003", "NFR-DATA-004")
@pytest.mark.parametrize(
    ("point", "raw_value", "expected_words"),
    [
        # I32 BIG: -100000 W = 0xFFFE7960 -> high word first
        ("ess.p", -100000, [0xFFFE, 0x7960]),
        ("ess.p", 150000, [0x0002, 0x49F0]),
        # U16 scale 0.1: 55.1 % -> 551
        ("ess.soc", 55.1, [551]),
    ],
)
def test_encode_matches_hand_computed_words(bess_map, point, raw_value, expected_words):
    reg = bess_map.by_point[point]
    assert reg.encode(raw_value) == expected_words
    value, sentinel = reg.decode(expected_words)
    assert not sentinel
    assert value == pytest.approx(raw_value)


@pytest.mark.req("FR-INT-003", "NFR-DATA-005")
def test_sentinel_decodes_to_no_value(bess_map):
    """na_values -> (None, True): the poller then reports BAD_DEVICE without a value (07 §5.1.5)."""
    assert bess_map.by_point["ess.soc"].decode([0xFFFF]) == (None, True)
