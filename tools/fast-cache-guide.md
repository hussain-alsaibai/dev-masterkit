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
26/26 passing. Covers LRU eviction, TTL expiry, stale-while-revalidate,
concurrent access, async wrapping, atomic add, and TTL keepalive refresh.

## When NOT to Use
- Distributed systems (use Redis/Memcached)
- Persistence required (fast-cache is in-memory only)
- Per-process caches that need to be invalidated externally (no pub/sub)

## Last Verified: 2026-07-14

- Commit: `8389359` (field note; cache primitives remain at `29ee08b`)
- Verification: the cache-ROI guidance was recorded after reviewing the
  repository's cache and agent-workflow field reports; no code changed in
  this documentation-only commit.
