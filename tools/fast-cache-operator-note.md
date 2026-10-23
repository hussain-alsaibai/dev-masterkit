# fast-cache Operator Note — Leases, Cache ROI, and the v0.8.0 Fix

> Field notes for using fast-cache as a **budget and rate-limit control** in
> agent and cron workloads, plus the operator-lease pattern.

**Repo:** https://github.com/hussain-alsaibai/fast-cache
**Last verified:** 2026-10-23 (v0.8.0 API re-verified by run)
**See also:** `tools/fast-cache-v0.8.0-guide.md` for the release details.

## API Correction (2026-10-23)

The v0.8.0 core is `fast_cache.py` exporting `Cache` and `CacheStats`.
There is **no module-level `cache` object** — `from fast_cache import cache`
raises `ImportError`. Use `Cache(...)` directly:

```python
from fast_cache import Cache
cache = Cache(maxsize=1024, ttl=300)
```

`add()` and `update()` are **not** on the v0.8.0 `Cache` class
(`dir(Cache)` verified 2026-10-23). The atomic-claim pattern below uses
`get_or_set()` plus an explicit lock if a strict first-writer-wins claim is
required, or the `SingleFlightCache` in `_v072.py` when the goal is to share
one factory call across concurrent misses.

## Cache ROI Checklist

For agent and cron workloads, treat caching as a budget and rate-limit
control, not only a latency optimization:

- Include repository, provider, query, and permission mode in cache keys.
- Record whether each result was live, fresh-cache, or stale-cache data.
- Use `info()` to review hits, misses, evictions, and avoided provider calls
  before increasing cache duration.
- Prefer bounded local caches for short-lived metadata lookups; do not cache
  tokens, private messages, or destructive-action decisions.
- Label stale values in user-facing summaries so freshness is never hidden.

## Operator Lease Caches

For local cron jobs, webhook receivers, bounty scanners, and repo updaters,
use `get_or_set()` as a short-lived first-writer-wins lease. Refresh long work
by re-writing the key, and delete the lease when the run ends if duplicate
suppression does not need to survive completion.

```python
from fast_cache import Cache

leases = Cache(maxsize=512, ttl=900)

def run_once(job_id: str, target: str) -> str:
    key = ("lease", job_id, target)
    if leases.get(key) is not None:
        return "skipped: already running"
    leases.set(key, {"status": "running"}, ttl=900)

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

**Note:** `get()` + `set()` is not atomic. For a true first-writer-wins claim
across threads, use `SingleFlightCache.get_or_set()` from `_v072.py` — it
serialises the factory call per key and shares the result with waiters.

## Stampede Protection (`SingleFlightCache`, v0.7.2)

```python
from fast_cache._v072 import SingleFlightCache

cache = SingleFlightCache(default_ttl=300)

# 100 concurrent calls for user_id=42 -> factory runs once, 99 share the result
results = [cache.get_or_set(("user", 42), lambda: load_user(42)) for _ in range(100)]

print(cache.stats.as_dict())
# {"loads": 1, "shared": 99, "waiters": 99, "peak_waiters": 99}
```

### The threading.Event invariant that's easy to get wrong

If the factory raises an exception, the in-flight slot MUST be cleared (and the
`Event` set), otherwise every future caller for that key hangs forever waiting
on a dead `Event`. This is the same class of bug as the v0.7.1 CRDT slot bug
in the same repo — **"fail fast, free the slot" is the family-wide
invariant.** Verify by looking at `SingleFlightStats.shared`; if it's >0 under
steady-state load, the protection is actually firing.

## Why This Matters

Cache stampedes are the production failure mode that nobody catches in dev: a
popular key expires under load, 1000 simultaneous requests all miss, all 1000
hit the slow backend, the backend gets 1000x its normal traffic. Single-flight
is the universal fix — Go's `singleflight` package (since 2014) and Java's
`LoadingCache.get(key, loader)` (Guava, since 2010) both ship it.

## The `info()` Deadlock — Do Not Copy the Old Pattern

Before v0.8.0, `Cache.info()` deadlocked permanently: `CacheStats.to_dict()`
held a plain `threading.Lock` and then called `self.hit_rate`, which re-acquired
the same lock. Any thread calling `info()` hung forever with no error.

v0.8.0 fixes it (`RLock` + inline `hit_rate`). If you are pinned to an older
version, the workaround is to read `cache.stats().hits` and
`cache.stats().misses` directly instead of calling `info()`.

**Last verified:** 2026-10-23
