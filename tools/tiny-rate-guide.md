# tiny-rate — Token Bucket, Fixed & Sliding Window Rate Limiter

## Repo
https://github.com/hussain-alsaibai/tiny-rate

## What It Does

Zero-dependency rate limiter with three algorithms: token bucket, fixed window, and sliding window. Sync + async. Decorator-based.

## When to Use

- Protecting APIs from overuse
- Throttling agent tool calls to stay within provider RPM/TPM limits
- Enforcing per-user request quotas

## Key Features

- **Token bucket**: smooth rate with burst capacity
- **Fixed window**: simple per-time-window counters
- **Sliding window**: smoothest rate limiting (no boundary spikes)
- Sync + async function support
- Per-key isolation (user ID, API key, IP address)
- Configurable callbacks on limit exceeded

## Quick Start

```python
from tiny_rate import rate_limit, TokenBucket

limiter = TokenBucket(capacity=10, refill_rate=2.0)  # 2 tokens/sec, burst 10

@rate_limit(limiter)
def call_llm(prompt):
    return openai_complete(prompt)
```

## Last Verified
2026-07-23
