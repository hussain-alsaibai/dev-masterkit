# tiny-bulkhead

> Zero-dependency concurrency isolation (bulkhead) for LLM calls.

A bulkhead caps the number of in-flight calls to a slow or failing dependency so
one stuck provider cannot starve every other call site. Composes with
`tiny-circuit-breaker` for full resilience:

- **bulkhead** = "do not queue too many"
- **circuit breaker** = "stop calling when the error rate is high"

## Install

```bash
pip install tiny-bulkhead
```

Or copy the single file `tiny_bulkhead.py` (~290 LOC) into your project.

## Quick start

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

# Or use the run() helper
result = pool.bulkhead("openai").run(openai_call, prompt="hi")
```

## Async support

```python
import asyncio
from tiny_bulkhead import Bulkhead

bh = Bulkhead("openai", max_concurrent=4)

async def go():
    async with bh():
        return await openai_async_call()

    # or use run_async
    return await bh.run_async(openai_async_call, prompt="hi")

asyncio.run(go())
```

## API

### `Bulkhead(name, max_concurrent, *, timeout=1.0, call_timeout=None)`

- `max_concurrent`: hard cap on in-flight calls (>= 1).
- `timeout`: seconds to wait for a slot. `0` = raise immediately if full.
  `None` = wait forever (rarely what you want).
- `call_timeout`: optional soft cap on the wrapped call (not enforced
  by the bulkhead itself; the call runs as long as it likes once a
  slot is held).

Methods:

- `acquire()` / `release(success=True)` / context-manager protocol.
- `run(func, *args, **kwargs)` — acquire, call, release, re-raise.
- `acquire_async()` / `release_async()` / `run_async()` for asyncio.
- `stats()` returns a `BulkheadStats` snapshot (JSON-serializable).
- `reset_stats()`.

Exceptions:

- `BulkheadFull` — slot not available within `timeout`.
- `BulkheadTimeout` — stub for a future per-call timeout.

### `BulkheadPool(sizes, *, default_timeout=1.0, default_call_timeout=None)`

A registry of named bulkheads sharing one global lock for stats.

- `sizes`: dict or iterable of `(name, max_concurrent)` pairs.
- `register(name, max_concurrent)` — add a bulkhead after construction.
- `bulkhead(name)` — look up a bulkhead (raises `KeyError` if unknown).
- `names()` — sorted list of registered names.
- `stats()` — `{name: BulkheadStats}` snapshot.

## Why a bulkhead?

When a provider goes slow, every request thread ends up blocked on
the same socket.  A bulkhead caps the number of in-flight calls per
provider, so a slow `openai` cannot exhaust the entire worker's
thread pool.

Pair with `tiny-circuit-breaker` to *also* fail fast when the error
rate is high, and with `tiny-rate-limiter` to bound the request rate
before either of them.  The three are independent levers:

| Pattern              | Question it answers                                |
|----------------------|----------------------------------------------------|
| Rate limiter         | "How many calls per second can we make?"           |
| Bulkhead             | "How many calls can be in flight at once?"         |
| Circuit breaker      | "Should we be calling at all right now?"           |

## License

MIT
