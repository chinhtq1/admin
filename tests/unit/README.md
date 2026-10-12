# tests/unit — L1 unit (marker `unit`, applied automatically)

Pure logic, no network/process/container I/O, < 1 s per test. One sub-directory per product component:
`bridge/` (edge/bridge/bridge), `ingest/`, `vsite/` (simulators/vsite/vsite), `regmap/` (shared codec),
`csms/`, `cli/` (tools/ems_cli.py), `framework/` (self-tests of tests/framework, no requirement tag).
Fakes over mocks: real `Store(tmp_path)`, fake Modbus client, `FakeClock` + `patch_module_time`.
Known bugs: `@pytest.mark.bug("A1-BUG-NN")` + `@pytest.mark.xfail(strict=True, reason=...)` asserting the *correct* behaviour.
