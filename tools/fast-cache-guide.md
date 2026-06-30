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
- **Stale-while-revalidate** — return stale value, refresh in background
  (prevents thundering herd)
- **Sync + async** — same decorator works on `def` and `async def`
- **Thread-safe** — uses `threading.RLock` internally
- **Stats** — `cache.stats()` returns hits, misses, evictions, hit rate

## Stale-While-Revalidate Pattern
```python
@cache(ttl=300, stale_ttl=3600)  # fresh for 5min, serve stale up to 1hr
def get_user_profile(user_id):
    return db.users.find_one(user_id)
```

When the entry is between `ttl` and `stale_ttl`, the cache returns the stale
value immediately and schedules a refresh in a background thread. The next
caller after refresh completes gets the new value.

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
18/18 passing. Covers LRU eviction, TTL expiry, stale-while-revalidate,
concurrent access, async wrapping.

## When NOT to Use
- Distributed systems (use Redis/Memcached)
- Persistence required (fast-cache is in-memory only)
- Per-process caches that need to be invalidated externally (no pub/sub)

## Last Verified: 2026-06-30