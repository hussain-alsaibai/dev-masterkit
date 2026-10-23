# tiny-rate — Token Bucket, Fixed & Sliding Window Rate Limiter

## Repo
https://github.com/hussain-alsaibai/tiny-rate

## What It Does

Zero-dependency rate limiter with three algorithms: token bucket, fixed window, and sliding window. Sync + async. Decorator-based.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_rate import rate_limit,
TokenBucket` and a `TokenBucket(capacity=10, refill_rate=2.0)` constructor.
**Both are wrong.** Verified against upstream `tiny_rate.py`:

```
__all__ = ['TokenBucket', 'FixedWindow', 'SlidingWindow', 'RateLimitExceeded',
           'limit', 'alimit', 'parse_rate']
```

The decorator is named **`limit`**, not `rate_limit`. The async variant is
**`alimit`**.

Constructor signatures (verified via `inspect.signature`):

```
TokenBucket(rate: float, capacity: Optional[float] = None)
limit(spec='10/s', *, algorithm='token', timeout=None, on_exceeded=None) -> Callable[[F], F]
alimit(...)  # async equivalent
parse_rate(spec) -> (count, per_seconds)
```

Note `TokenBucket` takes **`rate`** (tokens per second), not `capacity` /
`refill_rate`.

## Quick Start

```python
from tiny_rate import limit, TokenBucket

# Spec-string form (simplest)
@limit("10/s")
def call_llm(prompt):
    return openai_complete(prompt)

# Explicit object form
limiter = TokenBucket(rate=2.0, capacity=10)   # 2 tokens/sec, burst 10
```

`limit()` also accepts `algorithm='fixed'` and `algorithm='sliding'` to pick
`FixedWindow` / `SlidingWindow` instead of the token bucket.

## Related

- `tools/tiny-rate-limiter-guide.md` — `tiny-rate-limiter`, a separate repo
  with a different API (`rate_limit`, `TokenBucket`, `RateLimiter`)
- `tools/tiny-rate-window-guide.md` — `tiny-rate-window` (local only, not upstream)
- `tools/tiny-bucket-quota-guide.md` — `tiny-bucket-quota` (local only, not upstream)
- `tools/tiny-sliding-window-guide.md` — `tiny-sliding-window`
