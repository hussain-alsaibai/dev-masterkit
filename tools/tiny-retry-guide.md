# tiny-retry — Retry, Backoff & Circuit Breaker

## Repo
https://github.com/hussain-alsaibai/tiny-retry

## What It Does

Zero-dependency retry logic with exponential backoff, jitter, and circuit breaker pattern. Sync + async support. Decorator-based.

## When to Use

- Wrapping unreliable external API calls
- Protecting against transient network failures
- Implementing bulkhead/circuit-breaker for downstream services

## Key Features

- `@retry` decorator: configurable attempts, backoff, jitter
- `CircuitBreaker`: open/half-open/closed state machine
- Sync + async function support
- Built-in exception filtering
- Metrics: attempt count, last error, state

## Quick Start

```python
from tiny_retry import retry, CircuitBreaker

@retry(max_attempts=3, backoff=2.0, jitter=0.5)
def call_api(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

def safe_call(url):
    with breaker:
        return call_api(url)
```

## Last Verified
2026-07-23
