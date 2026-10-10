"""Register-map codec shared by the virtual site (encode) and the PoC edge bridge (decode).

One YAML file per driver (schema = subset of 07 §6.2). Both sides load the SAME file, so a map
error shows up as a wrong value in the cloud, not as two silently-consistent bugs on one side.
(R-15-01 still applies: a shared map cannot prove the map matches a real device.)

Value semantics: `raw_value (unit_raw) = (device_int * scale + offset) * sign_transform`
  - `scale` is a constant, or `scale_ref` names a SunSpec-style SF register: device_int * 10**SF.
  - `na_values` are sentinels compared on the device integer -> quality BAD_DEVICE.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# type -> (register count, signed)
_INT_TYPES = {
    "U16": (1, False), "I16": (1, True), "ENUM16": (1, False), "BITFIELD16": (1, False),
    "SUNSSF": (1, True), "U32": (2, False), "I32": (2, True), "BITFIELD32": (2, False),
    "U64": (4, False), "I64": (4, True),
}


@dataclass
class Register:
    point: str
    address: int
    type: str
    fc: int = 3
    word_order: str = "BIG"            # BIG (ABCD) | LITTLE_WORD (CDAB)
    scale: float = 1.0
    scale_ref: str | None = None
    offset: float = 0.0
    sign_transform: int = 1
    na_values: list[int] = field(default_factory=list)
    kind: str = "measurement"          # measurement|counter|status|setting|alarm|nameplate
    access: str = "R"                  # R | RW | W
    unit_raw: str | None = None
    readback_ref: str | None = None
    register_wrap: int | None = None
    persist: str | None = None         # VOLATILE | NVM | UNKNOWN
    min_write_interval_ms: int | None = None
    sunspec: str | None = None         # e.g. "701.W" -> cross-checked against pysunspec2
    doc_ref: str | None = None
    evidence: str | None = None

    @property
    def count(self) -> int:
        if self.type.startswith("STRING"):
            return int(self.type[7:-1])
        if self.type in ("F32",):
            return 2
        return _INT_TYPES[self.type][0]

    @property
    def internal(self) -> bool:
        """Internal registers (scale factors, heartbeat) are not published as telemetry."""
        return self.point.startswith("_")

    # ---- integer <-> words -------------------------------------------------------------
    def to_words(self, dev_int: int | float) -> list[int]:
        n = self.count
        if self.type == "F32":
            words = list(struct.unpack(">HH", struct.pack(">f", float(dev_int))))
        else:
            v = int(dev_int) & ((1 << (16 * n)) - 1)
            words = [(v >> (16 * (n - 1 - i))) & 0xFFFF for i in range(n)]
        return words[::-1] if (self.word_order == "LITTLE_WORD" and n > 1) else words

    def from_words(self, words: list[int]) -> int | float:
        n = self.count
        w = list(words[:n])
        if self.word_order == "LITTLE_WORD" and n > 1:
            w = w[::-1]
        if self.type == "F32":
            return struct.unpack(">f", struct.pack(">HH", *w))[0]
        v = 0
        for x in w:
            v = (v << 16) | (x & 0xFFFF)
        if _INT_TYPES[self.type][1] and v & (1 << (16 * n - 1)):
            v -= 1 << (16 * n)
        return v

    # ---- engineering <-> device ----------------------------------------------------------
    def factor(self, sf: int | None) -> float:
        if self.scale_ref:
            return 10.0 ** (sf or 0)
        return self.scale

    def encode(self, raw_value: float, sf: int | None = None) -> list[int]:
        dev = (raw_value / self.sign_transform - self.offset) / self.factor(sf)
        return self.to_words(dev if self.type == "F32" else round(dev))

    def decode(self, words: list[int], sf: int | None = None) -> tuple[float | None, bool]:
        """Return (raw_value, is_sentinel)."""
        dev = self.from_words(words)
        if dev in self.na_values:
            return None, True
        val = (dev * self.factor(sf) + self.offset) * self.sign_transform
        if self.kind == "counter":
            return int(round(val)), False          # counters stay int64 Wh (07 §7.2)
        return (val if not isinstance(val, float) or not math.isnan(val) else None), False


@dataclass
class RegisterMap:
    driver_id: str
    version: str
    connection: dict
    registers: list[Register]
    meta: dict

    @property
    def by_point(self) -> dict[str, Register]:
        return {r.point: r for r in self.registers}

    def span(self) -> tuple[int, int]:
        lo = min(r.address for r in self.registers)
        hi = max(r.address + r.count for r in self.registers)
        return lo, hi

    def blocks(self) -> list[tuple[int, int, list[Register]]]:
        """Group readable registers into read blocks (<=125 regs, gaps <= max_gap)."""
        max_gap = int(self.connection.get("max_gap", 0))
        regs = sorted((r for r in self.registers if "R" in r.access), key=lambda r: r.address)
        out: list[tuple[int, int, list[Register]]] = []
        for r in regs:
            if out:
                start, end, members = out[-1]
                if r.address - end <= max_gap and r.address + r.count - start <= 125:
                    out[-1] = (start, max(end, r.address + r.count), members + [r])
                    continue
            out.append((r.address, r.address + r.count, [r]))
        return out

    def sf_of(self, reg: Register, image: dict[str, int]) -> int | None:
        return image.get(reg.scale_ref) if reg.scale_ref else None


def load_map(path: str | Path) -> RegisterMap:
    doc = yaml.safe_load(Path(path).read_text())
    defaults = doc.get("defaults", {})
    regs = [Register(**{**defaults, **r}) for r in doc["registers"]]
    meta = {k: v for k, v in doc.items() if k not in ("registers", "defaults")}
    return RegisterMap(doc["driver_id"], str(doc["version"]), doc.get("connection", {}), regs, meta)


def load_maps(directory: str | Path) -> dict[str, RegisterMap]:
    """Return {"driver_id@version": RegisterMap} for every *.yaml in directory."""
    maps = {}
    for p in sorted(Path(directory).glob("*.yaml")):
        m = load_map(p)
        maps[f"{m.driver_id}@{m.version}"] = m
    return maps
