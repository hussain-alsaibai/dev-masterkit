# tiny-idempotency — Stripe-Style Idempotency Keys

## Summary

Zero-dependency idempotency key implementation. Prevents duplicate operations when clients retry requests. Based on Stripe's idempotency key pattern.

## Quick Reference

- **Repo:** [hussain-alsaibai/tiny-idempotency](https://github.com/hussain-alsaibai/tiny-idempotency)
- **Lines of code:** ~280
- **Tests:** 15 (all passing)
- **Dependencies:** None (stdlib only)

## Core Concept

An idempotency key is a unique string (UUID, custom format) passed in a request header. The server stores the key + response. On retry, the same key returns the cached response without re-executing.

## Usage

### Server-side handler

```python
from tiny_idempotency import IdempotencyStore, idempotent

store = IdempotencyStore()  # In-memory (use Redis for production)

@idempotent(store=store, ttl=86400)
def process_payment(request, key):
    # This only runs once per idempotency key
    return {"status": "charged", "amount": 100}
```

### Client-side retry

```python
import uuid, requests

headers = {"Idempotency-Key": str(uuid.uuid4())}
response = requests.post("/payments", json=data, headers=headers)

# On retry, use the SAME key
response = requests.post("/payments", json=data, headers=headers)
# Returns cached response, no duplicate charge
```

## IdempotencyStore Backends

### In-Memory (dev)

```python
store = IdempotencyStore()  # Lost on restart
```

### Redis (production)

```python
from tiny_idempotency import RedisIdempotencyStore

store = RedisIdempotencyStore(host="localhost", port=6379, key_prefix="idempotency:")
```

### TTL

```python
store = IdempotencyStore(ttl=86400)  # 24-hour key expiry
```

## Last Verified

2026-08-08
