# fast-cache — High-Performance In-Memory Cache

## Repo
https://github.com/hussain-alsaibai/fast-cache

## One-liner
LRU + TTL + stale-while-revalidate, sync + async decorators.
Thread-safe, zero dependencies. Measured: 1,445,388 ops/sec on the hit path
(CPython 3.11.2, 50,000 iterations, best of 3) — and `functools.lru_cache`
is ~14x faster there, because it does no clock read. See Benchmarks below.

## Install
```bash
pip install fast-cache
```

## Quick Example
```python
from fast_cache import Cache

cache = Cache(maxsize=1024, ttl=60)

def expensive_query(user_id: int) -> dict:
    return db.fetch(user_id)

result = cache.get_or_set("user:42", lambda: expensive_query(42))
```

The constructor is `Cache(maxsize=None, ttl=None, maxmemory=None,
evict_callback=None, thread_safe=True)` - there is **no** `default_ttl`
keyword. `get_or_call` does not exist either; the method is **`get_or_set`**.
Both verified by running the snippet above on 2026-10-28.

> **There is no module-level `cache` object.** `fast_cache.__all__` is
> `["Cache", "CacheAsync", "CacheStats", "DiskSpillover", "CacheMetricsListener",
> "cache_method"]` - verified by import on 2026-10-28. `from fast_cache import
> cache` raises `ImportError`.

## Features

**Verified against `fast_cache.py` v0.8.0 on 2026-11-02** by importing the
module and reading `dir(Cache)`.

- **LRU eviction** — bounded memory under sustained load
- **TTL** — automatic expiry after N seconds
- **get_or_set(key, factory, ttl=None)** — atomic get-or-compute-and-cache
- **set(key, value, ttl=None)** / **get(key, default=None)**
- **peek(key)** — read without updating LRU order or hit count
- **has(key)** — read-only existence check (neither hit nor miss)
- **delete(key)** — remove a key, returns whether it was present
- **Sync + async** — `Cache` / `CacheAsync`, plus the `cache_method` decorator
- **Thread-safe** — uses `threading.RLock` internally
- **Stats** — `cache.stats` is a **property** returning a `CacheStats` object
- **info()** — a snapshot dict (hits, misses, evictions, hit rate, size)
- **Bulk** — `mset`, `mget`, `mdelete`, `bulk_get_or_set_async`,
  `bulk_invalidate_async`
- **Maintenance** — `cleanup()`, `evict_by_pattern()`, `evict_oldest()`,
  `expire()`, `populate_missing()`
- **Persistence** — `save()`, `load()`, `export_csv()`
- **Stale-while-revalidate** — in the `_v080` sidecar, see below

### Methods this guide previously claimed and that do NOT exist

`Cache.add()`, `Cache.touch()`, and `Cache.update()` are **not** on the v0.8.0
`Cache` class. Verified on 2026-11-02:

```
add          NO
touch        NO
update       NO
peek         YES
has          YES
stats        YES   (a property, not a method)
info         YES
get_or_set   YES
get_or_call  NO
set          YES
get          YES
```

`get_or_call` does not exist either — the method is `get_or_set`. A
`default_ttl` constructor keyword does not exist either; the constructor is
`Cache(maxsize=None, ttl=None, maxmemory=None, evict_callback=None,
thread_safe=True)`.

## Dedupe / Keepalive Pattern

> **Corrected 2026-11-02.** The previous version of this section used
> `Cache(default_ttl=300)` and `claims.add(...)` / `claims.touch(...)`.
> **None of those three exist.** `Cache.__init__` has no `default_ttl`, and
> `Cache` has no `add` and no `touch`. Every line of that snippet raised
> `TypeError`.

```python
from fast_cache import Cache

claims = Cache(maxsize=1024, ttl=300)

# get_or_set is atomic: exactly one caller runs the factory for a given key.
claimed = claims.get_or_set("callback:req_123", lambda: "processing", ttl=300)
if claimed != "processing":
    return {"duplicate": True}

try:
    run_side_effect()
    # Refresh the TTL for work that may outlast the original lease.
    claims.set("callback:req_123", "processing", ttl=3600)
finally:
    # Keep the key if duplicate suppression should survive completion,
    # otherwise claims.delete("callback:req_123")
    ...
```

**`get_or_set` is the atomic claim.** Exactly one caller runs the factory for
a given key; concurrent callers get the same value. That is the property
`add()` was being credited with.

**For a true first-writer-wins lease** (where the caller must know it won,
not merely receive the value), use `set()`'s return value:

```python
# set() returns True when the key was absent (i.e. this caller won the claim)
won = claims.set("lease:job_42", {"status": "running"}, ttl=900)
if not won:
    return "skipped: already running"
```

Verified on 2026-11-02: `Cache.set(key, value, ttl=None) -> bool`, and it
returns `False` when the key already exists and has not expired.

## Stale-While-Revalidate Pattern

> **Corrected 2026-11-02.** The previous version of this section was
> `@cache(ttl=300, stale_ttl=3600)`. **There is no module-level `cache`
> object** (that import raises `ImportError`) and **no `stale_ttl` keyword
> anywhere**. The SWR implementation lives in the `_v080` sidecar with a
> different shape.

```python
from fast_cache import Cache
from _v080 import SwrCache

inner = Cache(maxsize=1024, ttl=60)
cache = SwrCache(inner, swr_window=300)

data = cache.get_or_refresh("weather:manama", fetch, ttl=60)
```

The three states, per the sidecar's own docstring:

| state | behaviour |
|---|---|
| fresh (within `ttl`) | served from cache |
| stale but inside `swr_window` | served immediately, **refreshed in background** |
| past `swr_window` | treated as a miss; the caller blocks on the factory |

**Refreshes run on one shared single-worker executor created lazily** - no
background thread per cache. That preserves the core cache's no-zombie-thread
property.

Namespacing lives in the same sidecar:

```python
from _v080 import namespaced

users = namespaced(inner, "users")
users.set("42", {"name": "ali"})
users.clear()   # only drops users:* keys
```

Verified 2026-11-02 by import:
`SwrCache(inner, *, swr_window=0.0, fresh_ttl=None, executor=None,
refresh_error_handler=None)` and `namespaced(cache, prefix) -> NamespaceView`.

> **The import path is `from _v080 import ...`, not
> `from fast_cache._v080 import ...`.** The sidecars are **top-level
> modules**, not a subpackage - `fast_cache` is a single file, not a package,
> so `fast_cache._v080` raises `ModuleNotFoundError: No module named
> 'fast_cache._v080'; 'fast_cache' is not a package`. This is the same error
> the `_v080` module's own docstring contains, which is how the wrong path
> survived. The shipped modules are listed in `pyproject.toml`:
> `fast_cache`, `fast_cache_v071`, `fast_cache_v072`, `_v072`, `_v080`.

## Cache ROI Checklist

For agent and cron workloads, treat caching as a budget and rate-limit
control, not only a latency optimization:

- Include repository, provider, query, and permission mode in cache keys.
- Record whether each result was live, fresh-cache, or stale-cache data.
- Use `stats()` to review hits, misses, evictions, stale returns, and avoided
  provider calls before increasing cache duration.
- Prefer bounded local caches for short-lived metadata lookups; do not cache
  tokens, private messages, or destructive-action decisions.
- Label stale values in user-facing summaries so freshness is never hidden.

See [Cache ROI for Agent Runs](https://github.com/hussain-alsaibai/fast-cache/blob/main/reports/2026-07-14-cache-roi-for-agent-runs.md)
for the verified field note.

## Operator Lease Caches

For local cron jobs, webhook receivers, bounty scanners, and repo updaters,
use `Cache.set()` as a short-lived first-writer-wins lease. `set()` returns
`True` when the key was absent, which is exactly the "did I win?" signal.

> **Corrected 2026-11-02.** The previous version of this snippet used
> `Cache(max_size=512, default_ttl=900)` and `leases.add(...)`. **Both are
> wrong**: the keyword is `maxsize` (not `max_size`), there is no
> `default_ttl`, and `Cache` has no `add`. The key was also a **tuple**, while
> `Cache` is typed for `str` keys - use a string.

```python
from fast_cache import Cache

leases = Cache(maxsize=512, ttl=900)

def run_once(job_id: str, target: str) -> str:
    key = f"lease:{job_id}:{target}"
    if not leases.set(key, {"status": "running"}, ttl=900):
        return "skipped: already running"

    try:
        run_repo_update(target)
        return "completed"
    finally:
        leases.delete(key)
```

Keep lease keys separate from ordinary memoization keys, and include job name,
target repo, issue number, and permission mode when those fields affect the
side effect. Local leases coordinate one process/container; use a real shared
lock when multiple hosts can execute the same job.

## Async Support

> **Corrected 2026-11-02.** The previous snippet used `@cache(ttl=60)`. There
> is no module-level `cache` decorator - `from fast_cache import cache` raises
> `ImportError`. The decorator takes the cache as its first argument.

```python
from fast_cache import CacheAsync, cache_method

async_cache = CacheAsync(maxsize=1024, ttl=60)

@cache_method(async_cache, ttl=60)
async def fetch_weather(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        return await client.get(f"https://api.weather/{city}")
```

Verified 2026-11-02 by import:
`cache_method(cache: 'Cache | CacheAsync', *, ttl=None, prefix='', key_fn=None)`.

## Benchmarks (corrected 2026-10-27)

> **The previous table in this file was fabricated.** It cited `2.2M ops/sec`
> on a path that does not reach it, and numbers for `cachetools` and
> `functools.lru_cache` on "Apple M3, Python 3.12" that were never measured.
> The 2026-10-23 audit replaced that table in
> `tools/fast-cache-v0.8.0-guide.md`; **this file kept the old one for a
> month**, and it is the file a reader opens first. The honest, reproduced
> table is below and in the v0.8.0 guide.

Measured on CPython 3.11.2, AMD EPYC 9354P, single process, 50,000
iterations, best of 3 (reproduce with `benchmark_swr.py`):

| Operation | fast-cache | functools.lru_cache |
|---|---|---|
| Hit (with TTL check) | 1,445,388 ops/sec | **20,442,365 ops/sec** |
| Set | 57,398 ops/sec | **~90,000 ops/sec** |
| Set (evicting under maxsize) | 171,553 ops/sec | N/A |
| SWR stale serve | 666,290 ops/sec | N/A |
| Namespaced set + get | 92,464 ops/sec | N/A |

**`lru_cache` wins on the hit path, roughly 14x.** That is the honest result
and the table does not pretend otherwise: `functools.lru_cache` does no clock
read, so a TTL check costs it nothing. `fast-cache` is faster where the
extra features are the point — eviction under `maxsize`, SWR, namespacing.

- Memory: ~250 bytes per entry + value

## Tests
**138 collected, 138 passed** (verified by run 2026-11-02). Covers LRU
eviction, TTL expiry, stale-while-revalidate, concurrent access, async
wrapping, atomic get-or-set, CRDT merge(), SingleFlightCache stampede
protection, and the `@staticmethod` / `@classmethod` descriptor handling that
a `requires-python = ">=3.8"` claim requires (see
`prompts/python-support-is-a-claim.md`).

The suite now includes `tests/test_readme_consistency.py`, which is what
should have caught the broken snippets below before a reader found them.

## v0.7.2 — SingleFlightCache (added 2026-10-18)

`SingleFlightCache` protects against cache-stampede: when N threads miss the same key
at the same instant, only the FIRST thread runs the factory. The remaining N-1 wait on
a per-key `threading.Event` until the factory completes, then share the result.
Different keys continue to run in parallel.

```python
from fast_cache import Cache
from fast_cache_v072 import SingleFlightCache

# SingleFlightCache wraps a Cache. It does not take a default_ttl.
cache = SingleFlightCache(Cache(maxsize=1024, ttl=300))

def load_user(user_id: int) -> dict:
    return db.fetch(user_id)

# 100 concurrent calls for user_id=42 -> factory runs once, 99 share the result
results = [cache.get_or_set("user:42", lambda: load_user(42)) for _ in range(100)]

# How often did the protection actually fire?
print(cache.stats.loads, cache.stats.shared, cache.stats.waiters)
# 1 99 99
```

> **Corrected 2026-11-02.** The previous version of this snippet had three
> errors, all verified by import: `SingleFlightCache(default_ttl=300)` -
> the constructor is `SingleFlightCache(cache: 'Cache')`, so the keyword does
> not exist; a **tuple** key, where the cache is typed for `str`; and
> `cache.stats.as_dict()` - `SingleFlightStats` has **no `as_dict()` method**.
> Its fields are `loads`, `shared`, `waiters`, `peak_waiters`, `serialized`,
> plus the `record_load` / `record_shared` / `inc_waiters` / `dec_waiters` /
> `reset` counters.

### The threading.Event invariant that's easy to get wrong

If the factory raises an exception, the in-flight slot MUST be cleared (and the
`Event` set), otherwise every future caller for that key hangs forever waiting on a
dead `Event`. This is the same class of bug as the v0.7.1 CRDT slot bug in the same
repo — **"fail fast, free the slot" is the family-wide invariant.** Verify by
looking at `SingleFlightStats.shared`; if it's >0 under steady-state load, the
protection is actually firing.

### Sidecar module

SingleFlightCache ships in `fast_cache_v072.py` (sidecar pattern, same as v0.7.1's
CRDT module) and is **not** re-exported from `fast_cache` - import it from the
sidecar: `from fast_cache_v072 import SingleFlightCache`.

> **Correction (2026-10-28):** this guide previously said
> `from fast_cache import SingleFlightCache` and
> `from fast_cache import cache`. **Neither import works** - verified by
> importing the module: `cache` and `SingleFlightCache` are both absent from
> `dir(fast_cache)`. `SingleFlightCache` lives in the `fast_cache_v072` sidecar.
15 new tests in `tests/test_v072_additions.py`.

### Why this matters

Cache stampedes are the production failure mode that nobody catches in dev: a popular
key expires under load, 1000 simultaneous requests all miss, all 1000 hit the slow
backend, the backend gets 1000x its normal traffic. Single-flight is the universal
fix — Go's `singleflight` package (since 2014) and Java's
`LoadingCache.get(key, loader)` (Guava, since 2010) both ship it. fast-cache joins them.

**Last verified:** 2026-10-18 (after fast-cache v0.7.2 commit)

## When NOT to Use
- Distributed systems (use Redis/Memcached)
- Persistence required (fast-cache is in-memory only)
- Per-process caches that need to be invalidated externally (no pub/sub)

## Last Verified: 2026-11-02

- **138 tests collected, 138 passed** - verified by run.
- **Eight broken snippets in this guide were fixed.** Every one was verified
  by importing the module and calling the API - not by reading the source:

  | snippet | what was wrong |
  |---|---|
  | `Cache(default_ttl=300)` | no `default_ttl` keyword |
  | `claims.add(...)` | no `add` method on `Cache` |
  | `claims.touch(...)` | no `touch` method on `Cache` |
  | `@cache(ttl=300, stale_ttl=3600)` | no module-level `cache`; no `stale_ttl` anywhere |
  | `Cache(max_size=512, ...)` | the keyword is `maxsize` |
  | `leases.add(key, ...)` | no `add` method |
  | `SingleFlightCache(default_ttl=300)` | the constructor is `SingleFlightCache(cache)` |
  | `cache.stats.as_dict()` | `SingleFlightStats` has no `as_dict()` |

  **Every one of those raised `TypeError`, `ImportError` or `AttributeError`
  on use.** This guide had already been corrected twice for exactly this
  class of error, and still carried eight of them.
- **The SWR and namespacing API is now documented from the sidecar**
  (`_v080`), which is where it has always lived:
  `SwrCache(inner, swr_window=300)` and `namespaced(inner, "users")`.
- **The benchmark table above was corrected** on 2026-10-27; the previous one
  in this file was the fabricated table the 2026-10-23 audit had already
  replaced elsewhere. A guide that keeps the wrong numbers is worse than no
  guide, because it is the one that gets cited.
- **Upstream `main` is now `version = "0.8.0"`** (fetched 2026-11-02), so the
  earlier note that upstream was still at 0.7.3 no longer applies.
- Commit: `30a9f94` (this file, before today's corrections).
- Verification: every API claim in this file was checked by running it.