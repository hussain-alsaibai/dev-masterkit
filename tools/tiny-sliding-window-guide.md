# tiny-sliding-window — Sliding Window Rate Limiter

**Source:** [hussain-alsaibai/tiny-sliding-window](https://github.com/hussain-alsaibai/tiny-sliding-window)
**License:** MIT | **Language:** Python 3.8+ | **Last verified:** 2026-08-27

## When to use

- API rate limiting where fixed-window burst at boundaries is unacceptable
- GitHub API calls (60 req/min sliding window)
- Third-party APIs with strict sliding window limits
- Per-user or per-key throttling without Redis

## What it does

Zero-dependency sliding window rate limiter. Thread-safe, O(log n) using sorted timestamps, optional persistence. No Redis, no external service.

## Quick start

```python
from tiny_sliding_window import SlidingWindow

# 60 GitHub API calls per minute
github = SlidingWindow(limit=60, window=60.0, name="github")

for issue in issues:
    result = github.check()
    if result.allowed:
        fetch_issue(issue)
    else:
        time.sleep(result.retry_after)
```

## Why sliding window over fixed window?

Fixed window (`INCR` + `EXPIRE` in Redis) allows burst at window boundaries:
```
Window 1: 50 allowed ─────────────────────│
Window 2:                              │─ 50 allowed
Burst:  100 requests in 1 second at boundary
```

Sliding window smooths this — no burst at boundaries.

## Key features

- Pure Python, zero dependencies
- Thread-safe for concurrent use
- O(log n) with sorted timestamps
- Optional persistence via callbacks (JSON, SQLite, etc.)
- Deterministic — same inputs always produce same output

## SlidingWindow API

| Method | Description |
|--------|-------------|
| `check()` | Returns `CheckResult(allowed, remaining, retry_after)` |
| `acquire()` | Blocking acquire (waits if needed) |
| `reset()` | Clear all state |
| `hits` | Total hits counter |

## Comparison with tiny-rate-limiter

`tiny-rate-limiter` offers TokenBucket, LeakyBucket, FixedWindow, and SlidingWindow algorithms. `tiny-sliding-window` is a focused, dedicated sliding window implementation. Use `tiny-rate-limiter` if you need algorithm choice; use this if you specifically need sliding window behavior.

## Last Verified
2026-08-27
