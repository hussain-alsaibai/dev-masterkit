# tiny-idempotency — Zero-Dependency Stripe-Style Idempotency Keys

## Repo
https://github.com/hussain-alsaibai/tiny-idempotency

## One-liner
Idempotent execution decorator with fingerprint-based key reuse detection, atomic claim/complete/fail lifecycle, thread-safe in-memory store, and crash-resilient NDJSON file store. Stripe's idempotency keys in one file.

## Install
```bash
pip install tiny-idempotency
```

## Quick Example

```python
from tiny_idempotency import idempotent, InMemoryStore, KeyMismatch, InProgressError

store = InMemoryStore()

@idempotent(store=store, key_arg="key", ttl_seconds=86400)
def charge_card(key: str, amount_cents: int, currency: str = "USD"):
    return stripe.Charge.create(amount=amount_cents, currency=currency)

# First call: runs and stores result
charge_card(key="evt_42", amount_cents=1000)

# Replay (same key, same args): returns cached result without re-running
charge_card(key="evt_42", amount_cents=1000)

# Reuse with DIFFERENT args: raises KeyMismatch
charge_card(key="evt_42", amount_cents=9999)   # ❌ KeyMismatch

# Concurrent same-key call: raises InProgressError
charge_card(key="evt_43", amount_cents=2000)  # first call
charge_card(key="evt_43", amount_cents=2000)  # ❌ InProgressError (still running)
```

## Three lifecycle states

```
              claim (atomic)
   [empty] ────────────────► [in-progress]
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
              complete          fail           timeout
              (cached)        (re-runnable)   (re-runnable)
```

A failed call does **not** poison the cache — the next caller can retry.
This matches Stripe's behavior: only successful results are replayable.

## Stores

### `InMemoryStore`

```python
from tiny_idempotency import InMemoryStore
store = InMemoryStore()
```

- Thread-safe (`threading.Lock` per key)
- Single-process
- LRU-bounded (default 10k entries)
- TTL eviction

### `FileStore` — crash-resilient

```python
from tiny_idempotency import FileStore
store = FileStore("./idempotency", fsync=True)
```

- NDJSON file per state (`pending.jsonl`, `completed.jsonl`, `failed.jsonl`)
- Atomic writes via `os.replace` + optional `fsync`
- Cross-process safe (one writer per record)
- TTL = file mtime check at load

## Fingerprint

Each call computes `Fingerprint = SHA-256(qualname + args + kwargs)`. If the
same key is reused with a different fingerprint, `KeyMismatch` is raised.
This catches the "is the client confused or did they really mean to re-charge?"
case before it becomes a duplicate-charge ticket.

## Properties

| Property | How |
|----------|-----|
| Atomic claim | Compare-and-set under lock + state check |
| Key reuse detection | Fingerprint SHA-256 over (qualname, args, kwargs) |
| Concurrent safety | Per-key locks; `InProgressError` on conflict |
| Failed-call safety | Failures don't cache; next call retries |
| Cross-process | `FileStore` with `os.replace` |
| TTL | Configurable per-decorator; lazy eviction |

## Testing

- **23/23 tests passing**
- 7 test categories (basic claim, fingerprint, KeyMismatch, InProgressError,
  TTL eviction, FileStore atomicity, crash recovery)
- 0 dependencies, 0 transitive deps
- 1 file
- ~570 LOC

## Gotcha — `KeyMismatch` is the right error to surface

When a client sends the same idempotency key with different arguments, the
correct response is **not** to silently return the cached result (which would
be wrong) and **not** to run anyway (which would be the duplicate write).
Raise `KeyMismatch` and let the caller decide:

```python
try:
    result = charge_card(key=request.idempotency_key, amount=body.amount)
except KeyMismatch:
    return 409, {"error": "idempotency_key_reused_with_different_payload"}
```

This matches Stripe's contract: their API returns HTTP 400 in this case.

## Gotcha — failed calls don't cache

If `charge_card` raises `stripe.CardError`, the result is **not** stored.
The next caller with the same key retries the function.

This is correct: Stripe will sometimes return `card_declined`, the user fixes
their card, and resubmits with the **same** idempotency key. If you cached
the failure, the user would be permanently blocked.

## Gotcha — fingerprint uses qualname, not just args

If you have:

```python
@idempotent(store=store, key_arg="key")
def charge_card(key, amount): ...
```

and

```python
@idempotent(store=store, key_arg="key")
def refund_card(key, amount): ...
```

…calling both with the same `key` and `amount` does **not** collide,
because the qualname (`charge_card` vs `refund_card`) is part of the
fingerprint. This is what you want.

## Migration from raw key dedup

```python
# before — fragile
_seen_keys = set()

def charge_card(key, amount):
    if key in _seen_keys:
        return _cache[key]
    result = stripe.Charge.create(...)
    _seen_keys.add(key)
    _cache[key] = result
    return result

# after — robust
@idempotent(store=store, key_arg="key")
def charge_card(key, amount):
    return stripe.Charge.create(...)
```

## Related ecosystem

- **`tiny-queue`** — uses caller-supplied `job_id` for idempotent enqueue (no decorator)
- **`tiny-retry`** — retry loop + idempotent decorator = safe to retry
- **`tiny-trace`** — `trace_id` makes a good `key_arg` for distributed idempotency

Last verified: 2026-07-04