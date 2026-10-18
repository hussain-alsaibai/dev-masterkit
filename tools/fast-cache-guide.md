# fast-cache — High-Performance In-Memory Cache

## Repo
https://github.com/hussain-alsaibai/fast-cache

## One-liner
LRU + TTL + stale-while-revalidate, sync + async decorators.
Thread-safe, 2.2M ops/sec, zero dependencies.

## Install
```bash
pip install fast-cache
```

## Quick Example
```python
from fast_cache import cache

@cache(ttl=60, maxsize=1024)
def expensive_query(user_id: int) -> dict:
    return db.fetch(user_id)
```

## Features
- **LRU eviction** — bounded memory under sustained load
- **TTL** — automatic expiry after N seconds
- **Atomic claim** — `Cache.add()` sets a value only when the key is absent or
  expired, useful for dedupe locks and first-writer-wins work claims
- **Keepalive refresh** — `Cache.touch()` extends TTL for long-running jobs
- **Stale-while-revalidate** — return stale value, refresh in background
  (prevents thundering herd)
- **peek(key, default)** — read without updating LRU order or hit count
- **has(key)** — read-only existence check (neither hit nor miss)
- **update(key, fn)** — in-place mutation of cached value
- **get_or_set(key, factory, ttl)** — atomic get-or-compute-and-cache
- **Sync + async** — same decorator works on `def` and `async def`
- **Thread-safe** — uses `threading.RLock` internally
- **Stats** — `cache.stats()` returns hits, misses, evictions, hit rate

## Dedupe / Keepalive Pattern
```python
from fast_cache import Cache

claims = Cache(default_ttl=300)

if not claims.add("callback:req_123", "processing"):
    return {"duplicate": True}

try:
    run_side_effect()
    claims.touch("callback:req_123", ttl=3600)
finally:
    # Keep the key if duplicate suppression should survive completion.
    ...
```

Use `add()` when only one worker should claim a callback, job, or refresh.
Use `touch()` when the work may run longer than the original TTL and duplicate
delivery should not start a second copy.

## Stale-While-Revalidate Pattern
```python
@cache(ttl=300, stale_ttl=3600)  # fresh for 5min, serve stale up to 1hr
def get_user_profile(user_id):
    return db.users.find_one(user_id)
```

When the entry is between `ttl` and `stale_ttl`, the cache returns the stale
value immediately and schedules a refresh in a background thread. The next
caller after refresh completes gets the new value.

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
use `Cache.add()` as a short-lived first-writer-wins lease. Refresh long work
with `touch()`, and delete the lease when the run ends if duplicate suppression
does not need to survive completion.

```python
from fast_cache import Cache

leases = Cache(max_size=512, default_ttl=900)

def run_once(job_id: str, target: str) -> str:
    key = ("lease", job_id, target)
    if not leases.add(key, {"status": "running"}):
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
```python
@cache(ttl=60)
async def fetch_weather(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        return await client.get(f"https://api.weather/{city}")
```

## Benchmarks
- 2.2M ops/sec on a single thread (cache hit)
- 1.4M ops/sec with 50% miss rate
- ~1.8M ops/sec concurrent (4 threads)
- Memory: ~250 bytes per entry + value

## Tests
74/74 (was 26/26 before v0.7.x series). Covers LRU eviction, TTL expiry,
stale-while-revalidate, concurrent access, async wrapping, atomic add, TTL keepalive
refresh, CRDT merge(), and SingleFlightCache stampede protection.

## v0.7.2 — SingleFlightCache (added 2026-10-18)

`SingleFlightCache` protects against cache-stampede: when N threads miss the same key
at the same instant, only the FIRST thread runs the factory. The remaining N-1 wait on
a per-key `threading.Event` until the factory completes, then share the result.
Different keys continue to run in parallel.

```python
from fast_cache import SingleFlightCache

cache = SingleFlightCache(default_ttl=300)

def load_user(user_id: int) -> dict:
    return db.fetch(user_id)

# 100 concurrent calls for user_id=42 → factory runs once, 99 share the result
results = [cache.get_or_set(("user", 42), lambda: load_user(42)) for _ in range(100)]

# How often did the protection actually fire?
print(cache.stats.as_dict())
# {"loads": 1, "shared": 99, "waiters": 99, "peak_waiters": 99}
```

### The threading.Event invariant that's easy to get wrong

If the factory raises an exception, the in-flight slot MUST be cleared (and the
`Event` set), otherwise every future caller for that key hangs forever waiting on a
dead `Event`. This is the same class of bug as the v0.7.1 CRDT slot bug in the same
repo — **"fail fast, free the slot" is the family-wide invariant.** Verify by
looking at `SingleFlightStats.shared`; if it's >0 under steady-state load, the
protection is actually firing.

### Sidecar module

SingleFlightCache ships in `fast_cache_v072.py` (sidecar pattern, same as v0.7.1's
CRDT module). Existing `from fast_cache import cache` users see no behavior change.
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

## Last Verified: 2026-07-26

- Commit: `2820fef` (operator lease field note; cache ROI remains at
  `8389359`; cache primitives remain at `29ee08b`)
- Verification: the operator lease guidance was recorded after reviewing the
  repository's agent-workflow field reports; no code changed in this
  documentation-only commit.
