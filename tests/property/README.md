# tests/property — property-based (marker `property`)

Hypothesis invariants: aggregator windows (half-open, BAD -> no value, cov_ms), codec round trip per map,
BESS physics (sign, SOC direction, losses, taper), ack contiguity. Use `@settings(deadline=None)` only with a reason;
derandomize in CI via the hypothesis profile when added.
