"""Deterministic clocks for unit tests.

Product modules call `time.time()`, `time.monotonic()` and `asyncio.sleep()` directly
(A1 §6). Patching the global `time` module also breaks the asyncio event loop and pytest-timeout,
so these helpers patch only the *module attribute* (e.g. `bridge.commands.time`) with a proxy that
overrides the clock functions and delegates everything else to the real module.

    clock = FakeClock()
    patch_module_time(monkeypatch, vsite.model, clock)
    clock.advance(15.1)            # watchdog timeout elapses instantly
"""

from __future__ import annotations

import asyncio as _real_asyncio
import time as _real_time
from types import ModuleType
from typing import Any

DEFAULT_WALL_MS = 1_791_590_400_000  # 2026-10-10T00:00:00Z — fixed, so tests are reproducible


class FakeClock:
    """Wall clock (can step backwards, like NTP) and monotonic clock (never goes backwards)."""

    def __init__(self, wall_ms: int = DEFAULT_WALL_MS, monotonic_s: float = 1_000.0) -> None:
        self._wall_ns = int(wall_ms) * 1_000_000
        self._mono_ns = int(monotonic_s * 1e9)

    # time-module compatible API
    def time(self) -> float:
        return self._wall_ns / 1e9

    def time_ns(self) -> int:
        return self._wall_ns

    def monotonic(self) -> float:
        return self._mono_ns / 1e9

    def monotonic_ns(self) -> int:
        return self._mono_ns

    perf_counter = monotonic

    def now_ms(self) -> int:
        return self._wall_ns // 1_000_000

    # control
    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("advance() only moves forward; use step_wall() for wall-clock jumps")
        delta = int(seconds * 1e9)
        self._wall_ns += delta
        self._mono_ns += delta

    def step_wall(self, seconds: float) -> None:
        """Jump only the wall clock (positive or negative), e.g. an NTP step. Monotonic unchanged."""
        self._wall_ns += int(seconds * 1e9)

    def time_module_proxy(self) -> Any:
        return _TimeProxy(self)

    def asyncio_module_proxy(self) -> Any:
        return _AsyncioProxy(self)


class _TimeProxy:
    def __init__(self, clock: FakeClock) -> None:
        self._clock = clock

    def __getattr__(self, name: str) -> Any:
        if name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter"):
            return getattr(self._clock, name)
        return getattr(_real_time, name)


class _AsyncioProxy:
    """asyncio proxy whose sleep(n) advances the fake clock and yields once (no real waiting)."""

    def __init__(self, clock: FakeClock) -> None:
        self._clock = clock

    async def sleep(self, delay: float, result: Any = None) -> Any:
        self._clock.advance(max(0.0, float(delay)))
        await _real_asyncio.sleep(0)
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(_real_asyncio, name)


def patch_module_time(monkeypatch: Any, module: ModuleType, clock: FakeClock) -> None:
    """Replace `module.time` (the module's own reference) with a proxy bound to `clock`."""
    if not hasattr(module, "time"):
        raise AttributeError(f"{module.__name__} has no attribute 'time' to patch")
    monkeypatch.setattr(module, "time", clock.time_module_proxy())


def patch_module_asyncio_sleep(monkeypatch: Any, module: ModuleType, clock: FakeClock) -> None:
    """Replace `module.asyncio` with a proxy whose sleep() fast-forwards `clock`."""
    if not hasattr(module, "asyncio"):
        raise AttributeError(f"{module.__name__} has no attribute 'asyncio' to patch")
    monkeypatch.setattr(module, "asyncio", clock.asyncio_module_proxy())
