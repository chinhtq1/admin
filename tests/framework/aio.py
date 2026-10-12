"""Run coroutines from synchronous tests with an explicit timeout (no pytest-asyncio dependency)."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any


def run[T](coro: Coroutine[Any, Any, T], *, timeout: float = 10.0) -> T:
    """asyncio.run(...) bounded by `timeout` seconds; cancels and raises TimeoutError on expiry."""

    async def _bounded() -> T:
        return await asyncio.wait_for(coro, timeout)

    return asyncio.run(_bounded())
