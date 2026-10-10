"""Modbus polling per endpoint (one TCP connection = one sequential queue, 07 §6.5) + quality (07 §5.1.5, §6.9)."""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from regmap import RegisterMap

log = logging.getLogger("bridge.poller")

COMM_FAIL_LIMIT = 3          # timeouts before BAD_COMM


@dataclass
class Reading:
    value: float | None
    q: str
    ts_ms: int
    ts_src_ms: int | None = None


class EndpointPoller:
    def __init__(self, device: dict, regmap: RegisterMap, period_s: float, on_reading, on_device_event):
        self.device, self.map, self.period = device, regmap, period_s
        ep = device["endpoint"]
        self.unit = int(ep["unit_id"])
        self.client = AsyncModbusTcpClient(ep["host"], port=int(ep["port"]), timeout=1, retries=0)
        self.lock = asyncio.Lock()               # writes (commands, heartbeat) share the connection
        self.blocks = regmap.blocks()
        self.points = {p["code"]: p for p in device["points"]}
        self.ts_src_point = device.get("ts_src_point")
        self.image: dict[str, Reading] = {}
        self.last_good: dict[str, Reading] = {}
        self.fail_count = 0
        self.comm_ok = True
        self.on_reading, self.on_device_event = on_reading, on_device_event
        self.max_age_ms = 3000

    @property
    def device_id(self) -> str:
        return self.device["device_id"]

    async def run(self) -> None:
        while True:
            t0 = time.monotonic()
            try:
                await self.poll_once()
            except Exception:                    # keep polling whatever happens (PoC)
                log.exception("poll %s", self.device_id)
            await asyncio.sleep(max(0.05, self.period - (time.monotonic() - t0)))

    async def _read_all(self) -> tuple[dict[int, int] | None, str | None]:
        words: dict[int, int] = {}
        async with self.lock:
            if not self.client.connected:
                await self.client.connect()
                if not self.client.connected:
                    return None, "BAD_COMM"
            for start, end, _ in self.blocks:
                rr = await self.client.read_holding_registers(start, count=end - start, device_id=self.unit)
                if rr.isError():
                    code = getattr(rr, "exception_code", 0)
                    return None, ("BAD_CONFIG" if code in (1, 2, 3) else f"EXC_{code}")
                words.update({start + i: w for i, w in enumerate(rr.registers)})
        return words, None

    async def poll_once(self) -> None:
        ts = int(time.time() * 1000)
        try:
            words, err = await self._read_all()
        except (ModbusException, asyncio.TimeoutError, OSError) as ex:
            words, err = None, "BAD_COMM"
            log.debug("%s comm error %s", self.device_id, ex)
            self.client.close()
        if words is None:
            self._handle_error(err, ts)
            return
        self.fail_count = 0
        if not self.comm_ok:
            self.comm_ok = True
            self.on_device_event(self.device_id, "DEVICE_COMM", "RESTORED", ts, None)
        image = {}
        for r in self.map.registers:
            if r.address not in words:
                continue
            sf = None
            if r.scale_ref:
                sf_reg = self.map.by_point[r.scale_ref]
                sf = sf_reg.from_words([words[sf_reg.address]])        # SF read in the same cycle (07 §6.2)
            val, sentinel = r.decode([words[r.address + i] for i in range(r.count)], sf)
            image[r.point] = Reading(None, "BAD_DEVICE", ts) if sentinel else Reading(val, "GOOD", ts)
        ts_src = None
        if self.ts_src_point and image.get(self.ts_src_point) and image[self.ts_src_point].value is not None:
            ts_src = int(image[self.ts_src_point].value * 1000)
        for code, rd in image.items():
            rd.ts_src_ms = ts_src
            self.image[code] = rd
            if rd.q == "GOOD":
                self.last_good[code] = rd
            if code in self.points:
                self.on_reading(self.device_id, self.points[code], rd)

    def _handle_error(self, err: str, ts: int) -> None:
        """07 §5.1.5: exc 01/02/03 -> BAD_CONFIG; 04/06 -> hold last until max_age then UNCERTAIN_STALE;
        timeout -> after N failures BAD_COMM."""
        if err == "BAD_COMM":
            self.fail_count += 1
            if self.fail_count < COMM_FAIL_LIMIT:
                return                                           # tolerate a couple of misses
            q = "BAD_COMM"
            if self.comm_ok:
                self.comm_ok = False
                log.warning("%s: %d consecutive timeouts -> BAD_COMM", self.device_id, self.fail_count)
                self.on_device_event(self.device_id, "DEVICE_COMM", "LOST", ts, None)
        elif err == "BAD_CONFIG":
            q = "BAD_CONFIG"
        else:
            q = "UNCERTAIN_STALE"
        for code, p in self.points.items():
            last = self.last_good.get(code)
            if q == "UNCERTAIN_STALE" and last and ts - last.ts_ms <= self.max_age_ms:
                rd = Reading(last.value, "GOOD", ts)
            else:
                rd = Reading(None, q, ts)
            self.image[code] = rd
            self.on_reading(self.device_id, p, rd)

    async def write(self, point: str, value: float) -> str | None:
        """FC16 write of one map register (one PDU for multi-word values). Returns error string or None."""
        r = self.map.by_point[point]
        if "W" not in r.access:
            return "NOT_WRITABLE"
        async with self.lock:
            try:
                if not self.client.connected:
                    await self.client.connect()
                rr = await self.client.write_registers(r.address, r.encode(value), device_id=self.unit)
            except (ModbusException, asyncio.TimeoutError, OSError) as ex:
                return f"COMM:{ex.__class__.__name__}"
        return f"EXC_{rr.exception_code}" if rr.isError() else None

    async def read_point(self, point: str) -> float | None:
        r = self.map.by_point[point]
        async with self.lock:
            try:
                rr = await self.client.read_holding_registers(r.address, count=r.count, device_id=self.unit)
            except (ModbusException, asyncio.TimeoutError, OSError):
                return None
        if rr.isError():
            return None
        return r.decode(rr.registers)[0]
