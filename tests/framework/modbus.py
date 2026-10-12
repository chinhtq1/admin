"""Modbus TCP probe that reads/writes named points through a register-map YAML.

Uses the product codec (`regmap`) for convenience in integration/system tests. Codec correctness itself
must be tested with independent golden vectors (tests/unit/regmap, R-15-01), not with this helper.
"""

from __future__ import annotations

from typing import Any

from pymodbus.client import ModbusTcpClient

from framework import REPO_ROOT

MAPS_DIR = REPO_ROOT / "simulators" / "vsite" / "maps"


def load_register_map(name: str) -> Any:
    import regmap  # product module, on pythonpath via pyproject

    return regmap.load_map(MAPS_DIR / name)


class ModbusProbe:
    def __init__(
        self, host: str, port: int, register_map: Any, *, unit_id: int | None = None, timeout: float = 3.0
    ) -> None:
        self.map = register_map
        self.unit_id = unit_id if unit_id is not None else int(register_map.connection.get("unit_id", 1))
        self.client = ModbusTcpClient(host, port=port, timeout=timeout, retries=0)

    def __enter__(self) -> ModbusProbe:
        if not self.client.connect():
            raise ConnectionError(f"cannot connect to Modbus server {self.client.comm_params.host}")
        return self

    def __exit__(self, *exc: object) -> None:
        self.client.close()

    def read_words(self, address: int, count: int) -> list[int]:
        rr = self.client.read_holding_registers(address, count=count, device_id=self.unit_id)
        if rr.isError():
            raise OSError(f"Modbus read {address}+{count} failed: {rr}")
        return list(rr.registers)

    def read_point(self, point: str, sf: int | None = None) -> tuple[float | None, bool]:
        reg = self.map.by_point[point]
        return reg.decode(self.read_words(reg.address, reg.count), sf)

    def write_point(self, point: str, value: float, sf: int | None = None) -> Any:
        reg = self.map.by_point[point]
        return self.client.write_registers(reg.address, reg.encode(value, sf), device_id=self.unit_id)
