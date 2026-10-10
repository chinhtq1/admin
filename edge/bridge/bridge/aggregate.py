"""Windowed aggregation per sampling class (07 §6.5, §7.3).

C1: 1 s reads -> 5 s windows (avg/min/max/last/n) on stream c1;  C2 -> 60 s (c2);  C3 -> 300 s (c3);
C4 counters -> raw int64 every C4 period (c4);  C5 (alarm words) -> events on change, not telemetry.
`ts` = window start (UTC ms), window is [ts, ts + w). BAD windows carry no value (never 0).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

WINDOW_S = {"C1": int(os.getenv("W_C1_S", "5")), "C2": int(os.getenv("W_C2_S", "60")),
            "C3": int(os.getenv("W_C3_S", "300"))}
C4_PERIOD_S = int(os.getenv("C4_PERIOD_S", "60"))
STREAM = {"C1": "c1", "C2": "c2", "C3": "c3", "C4": "c4"}


@dataclass
class Window:
    start_ms: int
    n: int = 0
    total: float = 0.0
    vmin: float = float("inf")
    vmax: float = float("-inf")
    last: float | None = None
    last_q: str = "BAD_COMM"
    reads: int = 0


@dataclass
class Aggregator:
    poll_period_s: float = 1.0
    windows: dict = field(default_factory=dict)       # pid -> Window
    meta: dict = field(default_factory=dict)          # pid -> sampling class
    counters: dict = field(default_factory=dict)      # pid -> latest Reading (C4)
    c4_next_ms: int = 0

    def add(self, point: dict, reading) -> None:
        cls, pid = point["sampling_class"], point["pid"]
        self.meta[pid] = cls
        if cls == "C4":
            self.counters[pid] = reading
            return
        if cls not in WINDOW_S:
            return
        w_ms = WINDOW_S[cls] * 1000
        start = reading.ts_ms - reading.ts_ms % w_ms
        win = self.windows.get(pid)
        if win is None or win.start_ms != start:
            # previous window (if any) is closed by flush(); keep it until then
            if win is not None and win.start_ms < start:
                self.windows.setdefault(("closed", pid), []).append(win)
            win = self.windows[pid] = Window(start)
        win.reads += 1
        win.last_q = reading.q
        if reading.value is not None and reading.q.startswith("GOOD"):
            v = float(reading.value)
            win.n += 1
            win.total += v
            win.vmin, win.vmax, win.last = min(win.vmin, v), max(win.vmax, v), v

    def _sample(self, pid: int, win: Window, w_s: int) -> dict:
        if win.n == 0:
            return {"pid": pid, "ts": win.start_ms, "w": w_s, "q": win.last_q if win.last_q != "GOOD" else "BAD_COMM"}
        s = {"pid": pid, "ts": win.start_ms, "w": w_s, "avg": round(win.total / win.n, 3), "min": win.vmin,
             "max": win.vmax, "last": win.last, "n": win.n, "q": "GOOD"}
        expected = int(w_s / self.poll_period_s)
        if win.n < expected:
            s["cov_ms"] = int(win.n * self.poll_period_s * 1000)
        return s

    def flush(self, now_ms: int) -> dict[str, list[dict]]:
        """Return closed samples grouped by stream."""
        out: dict[str, list[dict]] = {}
        for key in [k for k in self.windows if isinstance(k, tuple)]:
            pid = key[1]
            cls = self.meta[pid]
            for win in self.windows.pop(key):
                out.setdefault(STREAM[cls], []).append(self._sample(pid, win, WINDOW_S[cls]))
        for pid, win in list(self.windows.items()):
            if isinstance(pid, tuple):
                continue
            cls = self.meta[pid]
            w_ms = WINDOW_S[cls] * 1000
            if now_ms >= win.start_ms + w_ms + 500:              # window over + 0.5 s grace
                out.setdefault(STREAM[cls], []).append(self._sample(pid, win, WINDOW_S[cls]))
                del self.windows[pid]
        # C4: latest counter value every C4 period (+ boundary flag right after each 5-min boundary)
        if now_ms >= self.c4_next_ms and self.counters:
            period = C4_PERIOD_S * 1000
            self.c4_next_ms = now_ms - now_ms % period + period
            for pid, rd in self.counters.items():
                s = {"pid": pid, "ts": rd.ts_ms, "q": rd.q}
                if rd.value is not None and rd.q.startswith("GOOD"):
                    s["raw"] = int(rd.value)
                    s["boundary"] = rd.ts_ms % 300_000 < 5_000
                if rd.ts_src_ms:
                    s["ts_src"] = rd.ts_src_ms
                out.setdefault("c4", []).append(s)
        return out
