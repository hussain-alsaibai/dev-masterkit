# tiny-sentinel Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-sentinel
**Last verified:** 2026-08-26
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

Three resilience primitives in one file (~300 lines):

1. **Circuit Breaker** — prevents cascading failures; half-open probe after N failures
2. **Rate Limiter** — token bucket, leaky bucket, sliding window, fixed window algorithms
3. **Timeout Wrapper** — deadline-based per-call timeouts using signal or threading

## When to use

Drop into any AI agent or script that calls external APIs. Replaces needing `pybreaker`, `slowapi`, and `timeout-decorator` separately.

## Quick start

```python
from tiny_sentinel import CircuitBreaker, RateLimiter, with_timeout

# Circuit breaker — opens after 5 failures, probes half-open every 30s
cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

@cb
def call_api():
    ...

# Rate limiter — 100 requests per minute sliding window
rl = RateLimiter(rate=100, window=60, algorithm="sliding_window")

@rl
def call_api():
    ...

# Timeout — 5 second deadline
@with_timeout(5.0)
def slow_call():
    ...
```

## Key features

- All three in one importable module
- Fully sync and async compatible
- Thread-safe
- Configurable algorithms per limiter type
- Stdlib only — no `pip install` needed for agents

## Integration pattern

```python
from tiny_sentinel import CircuitBreaker, RateLimiter, with_timeout

# Stack all three for maximum protection
cb = CircuitBreaker(failure_threshold=3)
rl = RateLimiter(rate=50, window=60)

def call_llm_api(endpoint, payload):
    @cb
    @rl
    @with_timeout(10.0)
    def _call():
        return requests.post(endpoint, json=payload)
    return _call()
```

## Notes

- Created 2026-08-26 as part of the tiny-* ecosystem
- MIT licensed, zero dependencies
- Tests included at `tests/`
