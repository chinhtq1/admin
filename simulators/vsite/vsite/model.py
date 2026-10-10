"""Physics of the virtual site: scenario clock, PV, load, BESS, POC + load meters.

Sign convention (05 / 07 §7.2): grid + = import, BESS + = discharge, PV >= 0. Raw W / Wh.
Energy integrates in SIMULATED time (clock.speed); device dynamics (BESS lag, watchdog) in WALL time.
"""
from __future__ import annotations

import csv
import logging
import math
import random
import time
from dataclasses import dataclass, field

log = logging.getLogger("vsite.model")


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class Clock:
    """Scenario clock: local seconds-of-day, advanced by wall dt x speed."""

    def __init__(self, speed: float = 1.0, start_local: str = "10:30"):
        self.speed = speed
        h, m = (int(x) for x in start_local.split(":"))
        self.t_sim = h * 3600.0 + m * 60.0

    def advance(self, dt_wall: float) -> float:
        dt_sim = dt_wall * self.speed
        self.t_sim = (self.t_sim + dt_sim) % 86400.0
        return dt_sim

    @property
    def local_hhmm(self) -> str:
        t = int(self.t_sim)
        return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


class Profile:
    """1-minute day profile (pvlib PV + factory load), linear interpolation."""

    def __init__(self, path: str):
        with open(path) as f:
            rows = list(csv.DictReader(f))
        self.pv = [float(r["p_pv_ac_w"]) for r in rows]
        self.load = [float(r["p_load_w"]) for r in rows]
        self.ghi = [float(r["ghi"]) for r in rows]

    def at(self, series: list[float], t_sim: float) -> float:
        i, frac = divmod(t_sim / 60.0, 1.0)
        i = int(i) % len(series)
        return series[i] * (1 - frac) + series[(i + 1) % len(series)] * frac


@dataclass
class Inverter:
    device_id: str
    share: float
    p_ac_max_w: float = 100_000.0
    p: float = 0.0
    q: float = 0.0
    e_total: float = 0.0
    p_limit_ena: int = 0
    p_limit_pct: float = 100.0
    t_cabinet: float = 35.0
    alarm_word: int = 0

    def values(self) -> dict:
        return {"pv_inverter.p": self.p, "pv_inverter.q": self.q, "pv_inverter.f": 50.0 + random.gauss(0, 0.01),
                "pv_inverter.e_total": self.e_total, "pv_inverter.state": 1 if self.p > 0 else 0,
                "pv_inverter.alarm_word": self.alarm_word, "pv_inverter.t_cabinet": self.t_cabinet,
                "pv_inverter.p_limit_ena": self.p_limit_ena, "pv_inverter.p_limit_pct": self.p_limit_pct}

    def on_write(self, point: str, value: float) -> None:
        if point == "pv_inverter.p_limit_pct":
            self.p_limit_pct = clamp(value, 0, 100)
        elif point == "pv_inverter.p_limit_ena":
            self.p_limit_ena = int(value)
        log.info("%s write %s=%s", self.device_id, point, value)

    def step(self, p_plant_avail: float, dt_sim: float) -> None:
        avail = p_plant_avail * self.share
        cap = self.p_ac_max_w * (self.p_limit_pct / 100.0 if self.p_limit_ena else 1.0)
        self.p = clamp(avail, 0.0, cap)
        self.q = 0.0
        self.e_total += self.p * dt_sim / 3600.0
        self.t_cabinet = 32.0 + 15.0 * self.p / self.p_ac_max_w


@dataclass
class Bess:
    """BESS 250 kW / 500 kWh: SOC integration with eta, BMS limits with taper, lag, watchdog."""
    device_id: str = "ess-01"
    e_nom_wh: float = 500_000.0
    p_rated_w: float = 250_000.0
    eta_c: float = 0.95
    eta_d: float = 0.95
    soc: float = 55.0                  # %
    soc_min: float = 10.0
    soc_max: float = 95.0
    taper_pct: float = 5.0             # CCL/DCL decrease linearly inside this band near limits
    tau_s: float = 1.5                 # first-order lag of PCS response (wall seconds)
    watchdog_s: float = 15.0           # heartbeat register must change within this time
    p: float = 0.0
    p_setpoint: float = 0.0
    heartbeat: int = 0
    e_charge: float = 0.0
    e_discharge: float = 0.0
    alarm_word: int = 0
    bms_derate_w: float | None = None  # fault injection: BMS publishes a lower limit
    state: int = 0                     # 0 STANDBY 1 RUNNING 2 FAULT 3 WATCHDOG_REVERT
    _hb_seen_at: float = field(default_factory=time.monotonic)
    _reverted: bool = False

    ALARM_HEARTBEAT_LOST = 0x0100

    def limits(self) -> tuple[float, float]:
        pch = self.p_rated_w * clamp((self.soc_max - self.soc) / self.taper_pct, 0.0, 1.0)
        pdis = self.p_rated_w * clamp((self.soc - self.soc_min) / self.taper_pct, 0.0, 1.0)
        if self.bms_derate_w is not None:
            pch, pdis = min(pch, self.bms_derate_w), min(pdis, self.bms_derate_w)
        return pch, pdis

    def values(self) -> dict:
        pch, pdis = self.limits()
        return {"ess.p": self.p, "ess.soc": self.soc, "ess.soh": 98.7, "ess.p_charge_max": pch,
                "ess.p_discharge_max": pdis, "ess.e_charge": self.e_charge, "ess.e_discharge": self.e_discharge,
                "ess.state": self.state, "ess.mode": 1, "ess.alarm_word": self.alarm_word,
                "ess.cell_t_max": 28.0 + abs(self.p) / self.p_rated_w * 6.0,
                "ess.cell_v_min": 3.20 + self.soc / 100 * 0.12, "ess.cell_v_max": 3.23 + self.soc / 100 * 0.12,
                "ess.p_setpoint": self.p_setpoint, "_ess.heartbeat": self.heartbeat,
                "ess.p_rated": self.p_rated_w, "ess.e_nom": self.e_nom_wh}

    def on_write(self, point: str, value: float) -> None:
        if point == "_ess.heartbeat":
            if int(value) != self.heartbeat:
                self.heartbeat = int(value)
                self._hb_seen_at = time.monotonic()
                if self._reverted:
                    self._reverted = False
                    self.alarm_word &= ~self.ALARM_HEARTBEAT_LOST
                    log.warning("ess-01 heartbeat resumed -> remote control available again")
        elif point == "ess.p_setpoint":
            self.p_setpoint = float(value)
            self._hb_seen_at = time.monotonic()      # a setpoint write also proves the EMS is alive
            log.info("ess-01 write p_setpoint=%+.0f W", value)

    def step(self, dt_wall: float, dt_sim: float) -> None:
        idle = time.monotonic() - self._hb_seen_at
        if idle > self.watchdog_s and not self._reverted:
            self._reverted = True
            self.alarm_word |= self.ALARM_HEARTBEAT_LOST
            log.warning("WATCHDOG ess-01: heartbeat unchanged for %.1f s (> %.0f s) -> p_setpoint %+.0f W := 0 W (safe default)",
                        idle, self.watchdog_s, self.p_setpoint)
            self.p_setpoint = 0.0
        pch, pdis = self.limits()
        cmd = clamp(self.p_setpoint, -pch, pdis)
        self.p += (cmd - self.p) * (1.0 - math.exp(-dt_wall / self.tau_s))
        if abs(self.p) < 1.0:
            self.p = 0.0
        e = abs(self.p) * dt_sim / 3600.0
        if self.p > 0:
            self.soc -= e / (self.eta_d * self.e_nom_wh) * 100.0
            self.e_discharge += e
        elif self.p < 0:
            self.soc += e * self.eta_c / self.e_nom_wh * 100.0
            self.e_charge += e
        self.soc = clamp(self.soc, 0.0, 100.0)
        self.state = 3 if self._reverted else (1 if self.p != 0 else 0)


@dataclass
class Meter:
    device_id: str
    p: float = 0.0
    q: float = 0.0
    e_import: float = 0.0
    e_export: float = 0.0
    clock_offset_s: int = 0
    alarm_word: int = 0

    def values(self) -> dict:
        return {"meter.p": self.p, "meter.q": self.q, "meter.u.l1": 231.0 + random.gauss(0, 0.3),
                "meter.u.l2": 230.5 + random.gauss(0, 0.3), "meter.u.l3": 231.4 + random.gauss(0, 0.3),
                "meter.f": 50.0 + random.gauss(0, 0.01), "meter.e_import": self.e_import,
                "meter.e_export": self.e_export, "meter.clock": int(time.time()) + self.clock_offset_s,
                "meter.alarm_word": self.alarm_word}

    def on_write(self, point: str, value: float) -> None:
        pass

    def integrate(self, p: float, q: float, dt_sim: float) -> None:
        self.p, self.q = p, q
        if p >= 0:
            self.e_import += p * dt_sim / 3600.0
        else:
            self.e_export += -p * dt_sim / 3600.0


class Site:
    """P_grid = P_load + P_ev + P_charge - P_pv - P_discharge  (== load + ev - pv - ess.p)."""

    def __init__(self, scenario: dict, profile: Profile, inverter_ids: list[str]):
        clk = scenario["clock"]
        self.clock = Clock(float(clk["speed"]), str(clk["start_local"]))
        self.profile = profile
        b = scenario["bess"]
        self.bess = Bess(**b)
        rng = random.Random(42)
        shares = [1.0 + rng.uniform(-0.03, 0.03) for _ in inverter_ids]
        norm = sum(shares)
        inv_max = float(scenario["pv"]["inverter_p_ac_max_w"])
        self.inverters = {d: Inverter(d, s / norm, inv_max) for d, s in zip(inverter_ids, shares)}
        self.meter_poc = Meter("meter-poc")
        self.meter_load = Meter("meter-load")
        self.p_load = 0.0
        self.p_ev = 0.0
        self._ev_at = 0.0
        self.ev_timeout_s = 30.0

    def set_ev(self, p_w: float) -> None:
        self.p_ev, self._ev_at = max(0.0, p_w), time.monotonic()

    @property
    def p_pv(self) -> float:
        return sum(i.p for i in self.inverters.values())

    def step(self, dt_wall: float) -> None:
        dt_sim = self.clock.advance(dt_wall)
        t = self.clock.t_sim
        p_plant = self.profile.at(self.profile.pv, t)
        for inv in self.inverters.values():
            inv.step(p_plant, dt_sim)
        self.p_load = self.profile.at(self.profile.load, t)
        if time.monotonic() - self._ev_at > self.ev_timeout_s:
            self.p_ev = 0.0
        self.bess.step(dt_wall, dt_sim)
        p_grid = self.p_load + self.p_ev - self.p_pv - self.bess.p
        self.meter_poc.integrate(p_grid, 0.25 * self.p_load, dt_sim)
        self.meter_load.integrate(self.p_load, 0.25 * self.p_load, dt_sim)

    def snapshot(self) -> dict:
        b = self.bess
        pch, pdis = b.limits()
        return {"clock_local": self.clock.local_hhmm, "speed": self.clock.speed,
                "p_pv_w": round(self.p_pv), "p_load_w": round(self.p_load), "p_ev_w": round(self.p_ev),
                "ess": {"p_w": round(b.p), "p_setpoint_w": round(b.p_setpoint), "soc_pct": round(b.soc, 3),
                        "p_charge_max_w": round(pch), "p_discharge_max_w": round(pdis), "state": b.state,
                        "heartbeat": b.heartbeat, "alarm_word": b.alarm_word},
                "p_grid_w": round(self.meter_poc.p),
                "balance_check_w": round(self.p_load + self.p_ev - self.p_pv - b.p - self.meter_poc.p),
                "meter_poc": {"e_import_wh": int(self.meter_poc.e_import), "e_export_wh": int(self.meter_poc.e_export)},
                "pv": {d: {"p_w": round(i.p), "limit_pct": i.p_limit_pct if i.p_limit_ena else 100}
                       for d, i in self.inverters.items()}}
