# tiny-rate-limiter Tool Guide

> Zero-dependency rate limiter for Python. Token bucket, leaky bucket, sliding window, fixed window. ~5M ops/s. Single file.

**Source:** [hussain-alsaibai/tiny-rate-limiter](https://github.com/hussain-alsaibai/tiny-rate-limiter)
**License:** MIT | **Language:** Python 3.8+ | **Last verified:** 2026-07-30

## When to use

- Rate-limiting API calls to avoid 429s
- Protecting downstream services from burst traffic
- Per-user or per-endpoint throttling in web servers
- Async API gateways
- Any scenario where you need rate limiting without pulling in a heavy dependency

## Quick start

```python
from rate_limiter import rate_limit, TokenBucket, RateLimiter, RateLimitExceeded

# Decorator (default: reject fast)
@rate_limit("100 per minute")
def call_api():
    return api.get("/endpoint")

# Decorator (block until allowed)
@rate_limit("10 per second", block=True)
def call_slow():
    return api.get("/slow")

# Direct API
limiter = TokenBucket("5000 per hour", capacity=20)
if limiter.try_acquire():
    handle_request()
else:
    return 429, "slow down"

# Context manager
from rate_limiter import limit
with limit("5 per second", algorithm="leaky_bucket"):
    expensive_operation()

# Async
from rate_limiter import AsyncRateLimiter, TokenBucket
limiter = AsyncRateLimiter(TokenBucket("100 per second"))
if await limiter.check():
    return await client.get(url)
```

## Algorithms

| Algorithm | ops/s | Memory | Best for |
|---|---|---|---|
| TokenBucket | ~5M | O(1) | APIs with bursty traffic (default) |
| FixedWindow | ~2.9M | O(1) | Cheap counter, lenient limits |
| LeakyBucket | ~2.1M | O(1) | Constant output rate, traffic shaping |
| SlidingWindow | ~600K | O(N) | Strict per-window accuracy |

## Rate spec syntax

```
"<count> per <period> <unit>"   or   "<count> / <unit>"
```
Units: `ms`, `s`, `sec`, `m`, `min`, `h`, `hour`, `d`, `day`

## Per-scope rate limiting

```python
limiters = {}  # user_id -> RateLimiter

def get_limiter(user_id):
    if user_id not in limiters:
        limiters[user_id] = RateLimiter("100 per minute")
    return limiters[user_id]

@app.route("/api")
def handler():
    if not get_limiter(session["user_id"]).try_acquire():
        return ("Too Many Requests", 429)
    return do_work()
```

## Class method rate limiting

```python
class Scraper:
    @rate_limit("10 per second", key=lambda self: self.domain)
    def fetch(self, url):
        return requests.get(url)
```

## Key patterns

- `check()` / `try_acquire()` — non-blocking, returns bool
- `acquire(blocking=True, timeout=5.0)` — wait with optional timeout
- `remaining` — quota left right now (property)
- `hits` / `denied` — counters for monitoring
- `reset()` — reset all state

## Caveats

- In-process only. For multi-process/multi-container, use Redis with `INCR` + `EXPIRE` and `tiny-rate-limiter` per process.
- SlidingWindow is O(N) in the limit — don't use for very high counts (>10K/hour).
- TokenBucket is the right default for most API scenarios.

## Ecosystem context

Part of the **tiny-*** zero-dependency Python ecosystem. All tools: tiny-agent, tiny-llm, tiny-memory, tiny-log, tiny-config, tiny-validator, tiny-router, tiny-stream, tiny-realtime, tiny-circuit, tiny-semaphore, tiny-store, tiny-workflow, tiny-rbac, tiny-eval, tiny-chain.
