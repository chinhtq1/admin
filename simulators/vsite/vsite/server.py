"""Modbus TCP exposure of the model: one pymodbus 3.15 SimDevice + server per device/port.

The `action` hook (called before every request) refreshes registers from the model through the
shared YAML map (regmap.encode), applies writes (regmap.decode -> device.on_write) and injects faults.
"""
from __future__ import annotations

import asyncio
import functools
import logging
from dataclasses import dataclass

from pymodbus.constants import ExcCodes
from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

from regmap import RegisterMap

log = logging.getLogger("vsite.server")


@dataclass
class Faults:
    """Fault state per device, set through the REST API."""
    comm_loss: bool = False          # no answer (client times out) -> edge BAD_COMM
    exception: int | None = None     # Modbus exception code to return (1,2,3,4,6...)
    frozen: bool = False             # registers stop updating (cloud FROZEN detection)
    sentinel: bool = False           # na_values on the wire -> edge BAD_DEVICE

    def active(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in (False, None)}


def sunspec_image(regmap: RegisterMap, serial: str) -> tuple[int, list[int]]:
    """Build the SunSpec 1/701/704 image with pysunspec2 and cross-check the YAML addresses."""
    import sunspec2.device as sd

    dev = sd.Device()
    base = int(regmap.connection.get("sunspec_base", 40000))
    addr, starts = base + 2, {}
    for mid in regmap.meta["applies_to"]["models"]:
        m = sd.Model(mid)
        dev.add_model(m)
        starts[mid] = addr
        addr += m.len
    common = dev.models[1][0]
    for k, v in {"Mn": "EMS-PoC", "Md": "VSITE-DER-100K", "Opt": "sim", "Vr": "0.1.0", "SN": serial, "DA": 1}.items():
        common.points[k].value = v
    m701, m704 = dev.models[701][0], dev.models[704][0]
    for k, v in {"W_SF": 1, "VA_SF": 1, "Var_SF": 1, "PF_SF": -2, "A_SF": -1, "V_SF": -1, "Hz_SF": -2,
                 "TotWh_SF": 0, "TotVarh_SF": 0, "Tmp_SF": -1, "ACType": 3, "St": 0, "InvSt": 0, "ConnSt": 1}.items():
        m701.points[k].value = v
    for k, v in {"WMaxLimPct_SF": 0, "WMaxLimPctEna": 0, "WMaxLimPct": 100}.items():
        m704.points[k].value = v
    raw = dev.get_mb()
    regs = [0x5375, 0x6E53] + [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2)] + [0xFFFF, 0]
    # Cross-check: every `sunspec: <model>.<point>` in the YAML must sit where pysunspec2 put it.
    for r in regmap.registers:
        if r.sunspec:
            mid, name = r.sunspec.split(".")
            expect = starts[int(mid)] + dev.models[int(mid)][0].points[name].offset
            if expect != r.address:
                raise SystemExit(f"map {regmap.driver_id}: {r.point} address {r.address} != SunSpec {r.sunspec} @ {expect}")
    return base, regs


class DeviceServer:
    def __init__(self, device_id: str, regmap: RegisterMap, model, port: int, unit_id: int, faults: Faults):
        self.device_id, self.map, self.model, self.port, self.unit_id = device_id, regmap, model, port, unit_id
        self.faults = faults
        self.rw = [r for r in regmap.registers if "W" in r.access]
        self.readable = [r for r in regmap.registers if "R" in r.access]
        if "sunspec_base" in regmap.connection:
            self.start, image = sunspec_image(regmap, serial=device_id)
            simdata = self._chunks(self.start, image)
            self.sf_static = True
        else:
            self.start = regmap.span()[0]
            simdata = [SimData(r.address, count=r.count, values=0, datatype=DataType.REGISTERS,
                               readonly="W" not in r.access) for r in regmap.registers]
            self.sf_static = False
        self.simdevice = SimDevice(id=unit_id, simdata=simdata, action=functools.partial(DeviceServer.action, self))

    def _chunks(self, start: int, image: list[int]) -> list[SimData]:
        """Whole image readable; only RW map registers writable (others -> exception 02)."""
        out, cur = [], start
        for r in sorted(self.rw, key=lambda r: r.address):
            if r.address > cur:
                out.append(SimData(cur, values=image[cur - start:r.address - start], datatype=DataType.REGISTERS, readonly=True))
            out.append(SimData(r.address, values=image[r.address - start:r.address - start + r.count], datatype=DataType.REGISTERS))
            cur = r.address + r.count
        out.append(SimData(cur, values=image[cur - start:], datatype=DataType.REGISTERS, readonly=True))
        return out

    def _sf(self, reg, regs, start) -> int | None:
        if not reg.scale_ref:
            return None
        sf_reg = self.map.by_point[reg.scale_ref]
        return sf_reg.from_words(regs[sf_reg.address - start:sf_reg.address - start + 1])

    def refresh(self, regs: list[int], start: int) -> None:
        vals = self.model.values()
        for r in self.readable:
            if r.point.startswith("_sf.") or r.point not in vals:
                continue
            words = r.encode(vals[r.point], self._sf(r, regs, start))
            if self.faults.sentinel and r.na_values:
                words = r.to_words(r.na_values[0])
            regs[r.address - start:r.address - start + r.count] = words

    async def action(self, fc, start, address, count, regs, values):
        f = self.faults
        if f.comm_loss:
            await asyncio.sleep(30)                      # never answer in time
            return ExcCodes.GATEWAY_NO_RESPONSE
        if f.exception:
            return ExcCodes(f.exception)
        if values is not None:
            end = address + len(values)
            touched = [r for r in self.rw if r.address < end and address < r.address + r.count]
            covered = sum(r.count for r in touched)
            if not touched or covered != len(values) or any(r.address < address or r.address + r.count > end for r in touched):
                return ExcCodes.ILLEGAL_ADDRESS          # partial 32-bit writes / RO area refused
            for r in touched:
                v, _ = r.decode(list(values[r.address - address:r.address - address + r.count]), self._sf(r, regs, start))
                self.model.on_write(r.point, v)
            return None
        if not f.frozen:
            self.refresh(regs, start)
        return None

    async def serve(self) -> None:
        server = ModbusTcpServer([self.simdevice], address=("0.0.0.0", self.port))
        log.info("device %s on :%d unit %d map %s@%s", self.device_id, self.port, self.unit_id,
                 self.map.driver_id, self.map.version)
        await server.serve_forever()
