# tests/system — integration and e2e (explicit marker required)

- `@pytest.mark.integration`: 1-2 components + ephemeral Mosquitto (`mqtt_broker`) / TimescaleDB, or a pymodbus server on a local port.
- `@pytest.mark.e2e`: attach to the running `emspoc` stack (`compose_stack`, `stack_db`, `mqtt_factory`); scenarios D1-D12.
Never start/stop the stack here; resilience tests do that (owner only). Isolate by unique `command_id` and time windows.
