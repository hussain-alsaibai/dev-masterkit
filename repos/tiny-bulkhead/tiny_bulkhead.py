"""
tiny-bulkhead - Zero-dependency concurrency isolation for LLM calls.

A bulkhead partitions a shared thread pool (or semaphore) so that one
slow / failing dependency cannot starve every other call site. Pattern
comes from the same resilience family as the circuit breaker, but
operates on *concurrency budget* rather than *failure rate*.

Two flavours ship in this single file:

* :class:`Bulkhead` - a named semaphore-style cap. ``acquire()`` blocks
  (or raises) once ``max_concurrent`` calls are in flight.
* :class:`BulkheadPool` - a registry of named bulkheads sharing a
  single lock; ``pool.bulkhead("openai").run(call)`` is the common
  call site.

Both are thread-safe and async-safe (``async with`` and ``await`` are
supported via :meth:`Bulkhead.run_async`).

    from tiny_bulkhead import Bulkhead, BulkheadPool, BulkheadFull

    bh = Bulkhead("openai", max_concurrent=4)
    with bh:
        call_openai(...)

    pool = BulkheadPool({"openai": 4, "anthropic": 2, "local": 8})
    with pool.bulkhead("openai"):
        call_openai(...)

Why a bulkhead?  When a provider goes slow, every request thread ends
up blocked on the same socket.  A bulkhead caps the number of in-flight
calls per provider, so a slow ``openai`` cannot exhaust the entire
worker's thread pool.  Combine with :mod:`tiny_circuit_breaker` for
rate-style resilience: bulkhead = "don't queue too many", circuit
breaker = "stop calling when the error rate is high".
"""
from __future__ import annotations

import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, TypeVar, Union

__all__ = [
    "Bulkhead",
    "BulkheadPool",
    "BulkheadFull",
    "BulkheadTimeout",
    "BulkheadStats",
]
__version__ = "0.1.0"

T = TypeVar("T")

# ---------------------------------------------------------------------------
# exceptions
# ---------------------------------------------------------------------------


class BulkheadFull(Exception):
    """Raised when ``acquire()`` cannot get a slot within ``timeout``."""


class BulkheadTimeout(Exception):
    """Raised when a call inside the bulkhead exceeds ``call_timeout``."""


# ---------------------------------------------------------------------------
# value types
# ---------------------------------------------------------------------------


class BulkheadStats:
    """Snapshot of bulkhead counters. Cheap to copy and JSON-serialise."""

    __slots__ = (
        "name",
        "max_concurrent",
        "in_flight",
        "acquired",
        "rejected",
        "timed_out",
        "completed",
        "failed",
        "wait_seconds_total",
        "wait_seconds_max",
    )

    def __init__(self, name: str, max_concurrent: int) -> None:
        self.name = name
        self.max_concurrent = max_concurrent
        self.in_flight = 0
        self.acquired = 0
        self.rejected = 0
        self.timed_out = 0
        self.completed = 0
        self.failed = 0
        self.wait_seconds_total = 0.0
        self.wait_seconds_max = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "in_flight": self.in_flight,
            "acquired": self.acquired,
            "rejected": self.rejected,
            "timed_out": self.timed_out,
            "completed": self.completed,
            "failed": self.failed,
            "wait_seconds_total": round(self.wait_seconds_total, 6),
            "wait_seconds_max": round(self.wait_seconds_max, 6),
        }

    def __repr__(self) -> str:
        return (
            f"BulkheadStats(name={self.name!r}, in_flight={self.in_flight}/"
            f"{self.max_concurrent}, acquired={self.acquired}, "
            f"rejected={self.rejected})"
        )


# ---------------------------------------------------------------------------
# core bulkhead
# ---------------------------------------------------------------------------


class Bulkhead:
    """A named concurrency cap. See README.md for details."""

    def __init__(
        self,
        name: str,
        max_concurrent: int = 8,
        *,
        timeout: Optional[float] = 1.0,
        call_timeout: Optional[float] = None,
    ) -> None:
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be >= 0 or None")
        if call_timeout is not None and call_timeout <= 0:
            raise ValueError("call_timeout must be > 0 or None")

        self.name = name
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.call_timeout = call_timeout

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._in_flight = 0
        self._acquired = 0
        self._rejected = 0
        self._timed_out = 0
        self._completed = 0
        self._failed = 0
        self._wait_seconds_total = 0.0
        self._wait_seconds_max = 0.0

    def __enter__(self) -> "Bulkhead":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release(success=exc_type is None)

    def __call__(self) -> "_AsyncBulkheadAdapter":
        return _AsyncBulkheadAdapter(self)

    def acquire(self) -> None:
        """Block until a slot is free or raise :class:`BulkheadFull`."""
        deadline = None if self.timeout is None else time.monotonic() + self.timeout
        with self._cond:
            while self._in_flight >= self.max_concurrent:
                if deadline is None:
                    self._cond.wait()
                else:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self._rejected += 1
                        raise BulkheadFull(
                            f"bulkhead {self.name!r} is full "
                            f"({self._in_flight}/{self.max_concurrent}); "
                            f"timed out after {self.timeout}s"
                        )
                    self._cond.wait(remaining)
            self._in_flight += 1
            self._acquired += 1

    def release(self, *, success: bool = True) -> None:
        with self._cond:
            if self._in_flight <= 0:
                return
            self._in_flight -= 1
            if success:
                self._completed += 1
            else:
                self._failed += 1
            self._cond.notify(1)

    async def acquire_async(self) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.acquire)

    async def release_async(self, *, success: bool = True) -> None:
        self.release(success=success)

    def run(
        self,
        func: Callable[..., T],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Acquire, call ``func``, release. Re-raises after release."""
        self.acquire()
        success = True
        try:
            return func(*args, **kwargs)
        except BaseException:
            success = False
            raise
        finally:
            self.release(success=success)

    async def run_async(
        self,
        func: Callable[..., Awaitable[T]],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        await self.acquire_async()
        success = True
        try:
            return await func(*args, **kwargs)
        except BaseException:
            success = False
            raise
        finally:
            await self.release_async(success=success)

    @property
    def in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    def stats(self) -> BulkheadStats:
        s = BulkheadStats(self.name, self.max_concurrent)
        with self._lock:
            s.in_flight = self._in_flight
            s.acquired = self._acquired
            s.rejected = self._rejected
            s.timed_out = self._timed_out
            s.completed = self._completed
            s.failed = self._failed
            s.wait_seconds_total = self._wait_seconds_total
            s.wait_seconds_max = self._wait_seconds_max
        return s

    def reset_stats(self) -> None:
        with self._cond:
            self._acquired = 0
            self._rejected = 0
            self._timed_out = 0
            self._completed = 0
            self._failed = 0
            self._wait_seconds_total = 0.0
            self._wait_seconds_max = 0.0


class _AsyncBulkheadAdapter:
    def __init__(self, bulkhead: Bulkhead) -> None:
        self._bulkhead = bulkhead

    async def __aenter__(self) -> Bulkhead:
        await self._bulkhead.acquire_async()
        return self._bulkhead

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._bulkhead.release_async(success=exc_type is None)


# ---------------------------------------------------------------------------
# pool
# ---------------------------------------------------------------------------


class BulkheadPool:
    """A registry of named bulkheads sharing one global lock."""

    def __init__(
        self,
        sizes=None,
        *,
        default_timeout: Optional[float] = 1.0,
        default_call_timeout: Optional[float] = None,
    ) -> None:
        self._lock = threading.Lock()
        self._bulkheads: Dict[str, Bulkhead] = {}
        self._default_timeout = default_timeout
        self._default_call_timeout = default_call_timeout
        if sizes is not None:
            for entry in _as_pairs(sizes):
                name, max_concurrent = entry
                self.register(name, max_concurrent)

    def register(self, name: str, max_concurrent: int) -> Bulkhead:
        with self._lock:
            if name in self._bulkheads:
                raise ValueError(f"bulkhead {name!r} already registered")
            bh = Bulkhead(
                name,
                max_concurrent,
                timeout=self._default_timeout,
                call_timeout=self._default_call_timeout,
            )
            self._bulkheads[name] = bh
            return bh

    def bulkhead(self, name: str) -> Bulkhead:
        with self._lock:
            try:
                return self._bulkheads[name]
            except KeyError as exc:
                raise KeyError(
                    f"bulkhead {name!r} is not registered; "
                    f"available: {sorted(self._bulkheads)}"
                ) from exc

    def names(self) -> list:
        with self._lock:
            return sorted(self._bulkheads)

    def stats(self) -> Dict[str, BulkheadStats]:
        with self._lock:
            return {name: bh.stats() for name, bh in self._bulkheads.items()}


def _as_pairs(sizes):
    if isinstance(sizes, dict):
        return list(sizes.items())
    return list(sizes)

