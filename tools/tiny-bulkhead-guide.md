# tiny-bulkhead Guide

> Zero-dependency concurrency isolation (bulkhead) for LLM calls. ~290 LOC, 23 tests, stdlib-only.

**Repo:** github.com/hussain-alsaibai/tiny-bulkhead
**Version:** 0.1.0 (2026-10-13)
**Author:** OpenClaw (autonomous cron, developer-tool-reports context)
**Status:** ✅ Initial release — 23/23 tests passing; pairs with `tiny-circuit-breaker` and `tiny-rate-limiter` to form the three-piece resilience family.

---

## What is it?

`tiny-bulkhead` is a single-file Python library (~290 LOC) that caps the number of in-flight calls to a named dependency (an LLM provider, a database, an API). When the cap is reached, new callers either block with a timeout or raise `BulkheadFull` immediately.

```python
from tiny_bulkhead import Bulkhead, BulkheadPool, BulkheadFull

# Single bulkhead
bh = Bulkhead("openai", max_concurrent=4, timeout=1.0)
with bh:
    response = openai_call()

# Pool of bulkheads (one per provider)
pool = BulkheadPool({"openai": 4, "anthropic": 2, "local": 8})
with pool.bulkhead("openai"):
    response = openai_call()
```

## Why does it exist?

When a provider goes slow, every request thread ends up blocked on the same socket. A bulkhead caps the number of in-flight calls per provider, so a slow `openai` cannot exhaust the entire worker's thread pool.

The pattern is named after ship bulkheads — a leak in one compartment cannot flood the whole ship. A bulkhead in software isolates one slow dependency from the rest of the call graph.

## The three-piece resilience family

`tiny-bulkhead` is the concurrency arm. The other two:

- **`tiny-rate-limiter`** — "How many calls per second can we make?" (token / leaky / sliding window).
- **`tiny-circuit-breaker`** — "Should we be calling at all right now?" (CLOSED → OPEN → HALF_OPEN FSM keyed on error rate).

| Pattern | Question it answers |
|---------|---------------------|
| Rate limiter | "How many calls per second?" |
| Bulkhead | "How many calls in flight at once?" |
| Circuit breaker | "Should we be calling at all right now?" |

Treating them as one knob loses the diagnostic information that makes a post-mortem possible. A rate limiter says "we exceeded our quota"; a bulkhead says "our threads are all blocked on the same socket"; a circuit breaker says "the error rate is 80%, stop calling."

## Usage

### Sync

```python
from tiny_bulkhead import Bulkhead, BulkheadFull

bh = Bulkhead("openai", max_concurrent=4, timeout=1.0)

try:
    with bh:
        response = openai_call()
except BulkheadFull:
    return fallback()
```

### Async

```python
import asyncio
from tiny_bulkhead import Bulkhead

bh = Bulkhead("openai", max_concurrent=4)

async def go():
    async with bh():
        return await openai_async_call()

asyncio.run(go())
```

### Pool pattern

```python
pool = BulkheadPool({"openai": 4, "anthropic": 2, "local": 8})

# Per-call site
with pool.bulkhead("openai"):
    response = openai_call()

# Aggregated stats
stats = pool.stats()  # {"openai": BulkheadStats(...), "anthropic": ...}
```

## API

### `Bulkhead(name, max_concurrent, *, timeout=1.0, call_timeout=None)`

- `max_concurrent` — hard cap on in-flight calls (>= 1).
- `timeout` — seconds to wait for a slot. `0` = raise immediately. `None` = wait forever.
- `call_timeout` — optional soft cap on the wrapped call (not enforced by the bulkhead; the call runs as long as it likes once a slot is held).

Methods:

- `acquire()` / `release(success=True)` / context-manager.
- `run(func, *args, **kwargs)` — acquire, call, release, re-raise.
- `acquire_async()` / `release_async()` / `run_async()` for asyncio.
- `stats()` returns a `BulkheadStats` snapshot (JSON-serializable).
- `reset_stats()`.

Exceptions:

- `BulkheadFull` — slot not available within `timeout`.
- `BulkheadTimeout` — stub for a future per-call timeout.

### `BulkheadPool(sizes, *, default_timeout=1.0, default_call_timeout=None)`

A registry of named bulkheads sharing one global lock for stats.

- `sizes` — dict or iterable of `(name, max_concurrent)` pairs.
- `register(name, max_concurrent)` — add a bulkhead after construction.
- `bulkhead(name)` — look up a bulkhead (raises `KeyError` if unknown).
- `names()` — sorted list of registered names.
- `stats()` — `{name: BulkheadStats}` snapshot.

## Composition with `tiny-circuit-breaker`

```python
from tiny_circuit_breaker import CircuitBreaker
from tiny_bulkhead import Bulkhead

cb = CircuitBreaker("openai", failure_threshold=5, recovery_timeout=30)
bh = Bulkhead("openai", max_concurrent=4)

def call_openai(prompt):
    with cb:                       # 1. are we allowed to call?
        with bh:                   # 2. is there a slot?
            return openai_call(prompt)
```

## When to use it

✅ Use a bulkhead when:

- You call out to multiple external providers and one going slow can starve the others.
- You have a fixed thread pool / connection pool and want to prevent one slow dependency from monopolising it.
- You want a clean place to add a `BulkheadFull` fallback (return cached, return default, return 503).

❌ Don't use a bulkhead when:

- You only call one provider and the bottleneck is elsewhere.
- You already have a working rate limiter that bounds the call rate sufficiently.
- The "slot" is not the bottleneck — a queue would work as well as a cap.

## License

MIT. Single file, zero dependencies.

**Last verified:** 2026-10-13
