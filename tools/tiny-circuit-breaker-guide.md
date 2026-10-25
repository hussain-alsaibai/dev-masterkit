# tiny-circuit-breaker Guide
**Last verified: 2026-10-25** — 25 tests passing, verified by run.

**tiny-circuit-breaker** — Zero-dependency Circuit Breaker.

- **Repo:** github.com/hussain-alsaibai/tiny-circuit-breaker
- **Install:** `pip install tiny-circuit-breaker` or copy `tiny_circuit_breaker.py`
- **Size:** ~250 LOC, 0 dependencies
- **Tests:** 25 passing (verified by run 2026-10-25 — the guide previously said 12)

## When to Use

When calling unreliable external services (APIs, databases, LLM providers). Prevents cascading failures by short-circuiting calls when a service is down. Use alongside `tiny-retry` for a complete resilience toolkit.

## Three States

```
CLOSED (normal)         OPEN (failing)          HALF-OPEN (testing)
──────────────────      ────────────────        ──────────────────
Calls pass through      Calls rejected           One call through
Failure count ↑         No calls allowed          ↓
  threshold →           recovery_timeout          Success threshold →
  OPEN               ←───────────────           CLOSED or OPEN
```

## Quick Start

```python
from tiny_circuit_breaker import CircuitBreaker, CircuitOpen

cb = CircuitBreaker(
    failure_threshold=5,   # Open after 5 consecutive failures
    recovery_timeout=30.0,   # Wait 30s before testing recovery
    success_threshold=2,   # Need 2 successes to close
    excluded=(ValueError,),  # Don't trip on these
)

# Context manager style
for i in range(100):
    with cb:
        result = risky_api_call()   # Auto-records success/failure

# Explicit call
try:
    result = cb.call(risky_api_call)
except CircuitOpen:
    print("Circuit is open — service unavailable")

# Stats
stats = cb.stats
print(f"Rejections: {stats.rejected_calls}, Failure rate: {stats.failure_rate:.1%}")
```

## Key Features

- Thread-safe (RLock)
- Configurable thresholds
- Excluded exception types
- Statistics tracking
- Manual `reset()`
- Context manager + explicit `call()` API
