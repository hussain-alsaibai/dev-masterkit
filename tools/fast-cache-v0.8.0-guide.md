# fast-cache v0.8.0 Guide — Deadlock Fixed, SWR Shipped, Honest Benchmarks

> Zero-dependency in-memory cache for Python. v0.8.0 fixes a **permanent
> deadlock in `Cache.info()`**, ships stale-while-revalidate and key
> namespacing, and replaces a fabricated benchmark table with measured
> numbers.

**Repo:** https://github.com/hussain-alsaibai/fast-cache
**Version:** 0.8.0 (2026-10-23)
**Install:** `pip install fast-cache` or copy `fast_cache.py`
**Size:** ~530 LOC core + `_v072.py` + `_v080.py` sidecars, 0 dependencies
**Tests:** 54 passing (verified by run, 2026-10-23)
**Last verified:** 2026-10-23

> **Upstream is behind.** `https://raw.githubusercontent.com/hussain-alsaibai/fast-cache/main/pyproject.toml`
> reports `version = "0.3.0"` (checked 2026-10-23), and upstream
> `fast_cache.py` still has the v0.8.0 deadlock (`CacheStats._lock =
> threading.Lock()` at line 71, with `to_dict()` calling `hit_rate()` under
> the same lock). **All v0.8.0 work is local and unpushed.** Do not read the
> upstream README as the current API.

## The Defect — `Cache.info()` Deadlocked Permanently

`CacheStats.to_dict()` acquired a plain `threading.Lock` and then called
`self.hit_rate`, which re-acquired the same lock. Every call to
`Cache.info()` hung the calling thread forever — no error, no timeout, no
traceback. The README's "check your hit rate" instruction was an infinite
hang.

It was found because the legacy test suite also hung: `test_info` never
returned. The suite printed all dots and then stopped.

**Fix:** `_lock` became a `threading.RLock`, and `hit_rate` is computed inline
so every counter is read under one acquisition.

### The general rule

> A plain `Lock` is not reentrant. If any method under the lock can reach
> back into another method that takes the same lock, you have a deadlock
> waiting for the first call. Two instances of this exact bug class appeared
> in two days across two repos (fast-cache `Cache.info()`, tiny-mcp-registry
> `export()`). **Use `RLock` whenever a lock may nest**, and snapshot under
> the lock then build the payload outside it.
>
> The symptom to watch for: the suite prints all dots then hangs forever at
> exit.

## Quick Start (verified API)

```python
from fast_cache import Cache

cache = Cache(maxsize=1000, ttl=3600)
cache.set("key", "value")
print(cache.get("key"))            # "value"
print(cache.info()["hit_rate"])    # now returns instead of hanging
```

Note the constructor signature — `maxsize`, not `max_size`:

```
Cache(maxsize=None, ttl=None, maxmemory=None, evict_callback=None, thread_safe=True)
```

Public methods (verified by `dir()` on v0.8.0):
`cleanup, clear, delete, expire, get, get_or_set, has, info, items, keys, load,
mdelete, memory_usage, mget, mset, pop, save, set, size, stats, ttl_remaining,
values`

## What Changed in v0.8.0

### 1. `SwrCache` — stale-while-revalidate with per-key coalescing

```python
from fast_cache import Cache
from fast_cache._v080 import SwrCache

inner = Cache(maxsize=100)
swr = SwrCache(inner, swr_window=300, fresh_ttl=60)

data = swr.get_or_refresh("weather:manama", fetch, ttl=60)
```

Three states, verified live on 2026-10-23:

| State | Behaviour |
|-------|-----------|
| inside `fresh_ttl` | return the cached value (`fresh_hit`) |
| inside the SWR window | serve the stale value **now**, refresh in the background (`stale_hit`) |
| past the window | block on the factory (`expired_miss`) |

Live trace (fresh_ttl=0.3s, swr_window=5s):

```
1 initial  -> fresh-1 calls=1     # expired_miss
2 fresh    -> fresh-1 calls=1     # fresh_hit, no refresh
3 stale    -> fresh-1 calls=2     # stale_hit, refresh scheduled
4 refreshed-> fresh-2 calls=2     # background refresh landed
stats -> {fresh_hit: 1, stale_hit: 2, expired_miss: 1, refreshes: 2, coalesced: 0}
```

At most one refresh per key runs at a time; concurrent callers during a
refresh are **coalesced** instead of stacking work (`coalesced` counter).
A failed background refresh keeps the previous value and calls
`refresh_error_handler(key, exception)` if one was supplied.

### 2. `namespaced()` — key-prefix isolation

```python
from fast_cache import Cache
from fast_cache._v080 import namespaced

cache = Cache(maxsize=100)
cache.set("a", 1)
users = namespaced(cache, "users")

users.get("a")     # None  - the namespace does not leak into the raw cache
users.set("a", 99)
cache.get("a")     # 1     - raw key untouched
cache.get("users:a")  # 99
```

Verified live on 2026-10-23. `NamespaceView` also provides `get_or_set`,
`add` (insert only when absent), `incr` (locks only the arithmetic), `delete`,
and `clear` (drops only `prefix:*` keys).

### 3. Honest benchmarks

The previous README benchmark table was **fabricated**: it cited cachetools and
`functools.lru_cache` numbers for SWR on "Apple M3, Python 3.12" that were
never measured, and claimed 2.2M ops/sec on a path that does not reach it.

`benchmark_swr.py` now reproduces every number in the table. Measured on
CPython 3.11.2, AMD EPYC 9354P, single process, 50,000 iterations, best of 3:

| Operation | fast-cache | functools.lru_cache |
|-----------|-----------|---------------------|
| Hit (with TTL check) | 1,445,388 ops/sec | **20,442,365 ops/sec** |
| Set | 57,398 ops/sec | **~90,000 ops/sec** |
| Set (evicting under maxsize) | 171,553 ops/sec | N/A |
| SWR stale serve | 666,290 ops/sec | N/A |
| Namespaced set + get | 92,464 ops/sec | N/A |

**lru_cache wins on the hit path, roughly 14x.** That is the honest result and
the table does not pretend otherwise: `functools.lru_cache` does no clock read,
no memory accounting, and no stats update.

Choose fast-cache when you need any of: TTL as part of the data model, size
or memory caps, observable stats (`cache.info()`), runtime mutation
(`expire()`, `invalidate()`, `save()`/`load()`), or zero dependencies in one
file. Choose `lru_cache` when you want the fastest possible memoization and
need none of the above.

### 4. Scalar fast path for size accounting

`_estimate_size` avoids `json.dumps` on every write when the value is a
scalar. `set` went **22K -> 57K ops/sec**; hits went **591K -> 1,445K**.

### 5. `SwrCache` + `namespaced()` in `_v080.py`

Shipped as a sidecar, following the family pattern. The sidecar docstring
records the defect it fixes:

> The README advertised SWR and namespacing from 2026-08-16, but neither
> existed in the code: there was no 'swr_ttl' parameter, no '@fc.cache'
> decorator, and no 'namespace=' argument. Any snippet copied from the README
> raised TypeError.

`from fast_cache import cache` **never worked** — `__all__ = ["Cache",
"CacheStats"]`, there is no module-level `cache` object. Any guide showing
`from fast_cache import cache` is wrong.

## Also in v0.8.0

- `SwrCache` (stale-while-revalidate, per-key coalescing)
- `namespaced()` + `NamespaceView`
- scalar fast path for `_estimate_size`
- 54 tests total (28 legacy + 26 new)

`SingleFlightCache` from v0.7.2 remains available in `_v072.py` for
cold-start stampede protection:

```python
from fast_cache._v072 import SingleFlightCache
```

## API Surface (verified)

```python
from fast_cache import Cache, CacheStats
from fast_cache._v072 import SingleFlightCache, SingleFlightStats
from fast_cache._v080 import SwrCache, SwrStats, namespaced, NamespaceView
```

## When NOT to Use

- Distributed systems (use Redis/Memcached)
- Persistence required across restarts beyond `save()`/`load()`
- Maximum raw speed on a pure hit path (`lru_cache` is 14x faster)

## The Transferable Lesson

> **A benchmark table that nobody measured is worse than no table.** It was
> the only asset a small library has — trust — and it was fabricated with
> plausible numbers on a machine that was never used. The fix was not
> "make the numbers better" but "make every number reproducible":
> `benchmark_swr.py` exists so the README can be regenerated from a run.
>
> And the honest version of the table is unflattering: `lru_cache` is 14x
> faster on a pure hit. Publishing that is what makes the other four rows
> believable.

See also `prompts/readme-claims-must-be-runnable.md` and
`reports/2026-10-23-developer-tools-landscape.md`.
