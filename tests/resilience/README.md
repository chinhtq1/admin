# tests/resilience — fault injection (marker `resilience`)

Broker down (D8), edge down / watchdog (D9), ingest down, DB down, Modbus faults via vsite REST, network faults via toxiproxy/iptables
(A3 §3.8). Stopping/starting services requires `EMS_TEST_OWN_STACK=1` (Docker stack owner only); nightly.
