"""Polling helpers with explicit timeouts.

Rule: never `time.sleep(n); assert ...`. Poll an observable condition until it holds or a deadline
passes, and report the last observed value on timeout so failures are diagnosable.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

_MISSING = object()


class WaitTimeout(AssertionError):
    """Raised when a condition did not hold before its deadline (an assertion failure, not an error)."""


class Deadline:
    def __init__(self, timeout: float, clock: Callable[[], float] = time.monotonic) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self._clock = clock
        self.timeout = timeout
        self.expires = clock() + timeout

    def remaining(self) -> float:
        return max(0.0, self.expires - self._clock())

    @property
    def expired(self) -> bool:
        return self._clock() >= self.expires


def wait_for_value[T](
    fn: Callable[[], T],
    predicate: Callable[[T], bool] = bool,
    *,
    timeout: float,
    interval: float = 0.1,
    desc: str = "condition",
    ignore: tuple[type[BaseException], ...] = (),
) -> T:
    """Call `fn` until `predicate(value)` is true; return that value or raise WaitTimeout."""
    deadline = Deadline(timeout)
    last: Any = _MISSING
    last_exc: BaseException | None = None
    attempts = 0
    while True:
        attempts += 1
        try:
            last = fn()
            last_exc = None
            if predicate(last):
                return last
        except ignore as exc:  # transient errors the caller expects (e.g. connection refused)
            last_exc = exc
        if deadline.expired:
            shown = "<no value>" if last is _MISSING else repr(last)[:500]
            extra = f"; last exception: {last_exc!r}" if last_exc else ""
            raise WaitTimeout(
                f"timed out after {timeout:.1f}s ({attempts} attempts) waiting for {desc}; last value: {shown}{extra}"
            )
        time.sleep(min(interval, deadline.remaining()) or 0)


def wait_until(
    fn: Callable[[], Any],
    *,
    timeout: float,
    interval: float = 0.1,
    desc: str = "condition",
    ignore: tuple[type[BaseException], ...] = (),
) -> Any:
    """Shorthand: wait until `fn()` is truthy."""
    return wait_for_value(fn, bool, timeout=timeout, interval=interval, desc=desc, ignore=ignore)


async def async_wait_for_value[T](
    fn: Callable[[], Awaitable[T]] | Callable[[], T],
    predicate: Callable[[T], bool] = bool,
    *,
    timeout: float,  # noqa: ASYNC109 - explicit per-call deadline is the point of this helper
    interval: float = 0.05,
    desc: str = "condition",
) -> T:
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    last: Any = _MISSING
    while True:
        value = fn()
        if asyncio.iscoroutine(value) or isinstance(value, asyncio.Future):
            value = await value
        last = value
        if predicate(value):
            return value
        if loop.time() >= end:
            shown = "<no value>" if last is _MISSING else repr(last)[:500]
            raise WaitTimeout(f"timed out after {timeout:.1f}s waiting for {desc}; last value: {shown}")
        await asyncio.sleep(interval)
