# tiny-circuit — Circuit Breaker for Fault Tolerance

## Repo
https://github.com/hussain-alsaibai/tiny-circuit

## One-liner
Zero-dep circuit breaker with CLOSED → OPEN → HALF_OPEN state machine. Protects against cascading failures in multi-step workflows.

## Install
```bash
pip install tiny-circuit
```

## Quick Example
```python
from tiny_circuit import circuit_breaker, Result

@circuit_breaker(failure_threshold=5, recovery_timeout=60)
async def call_api(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        return await client.get(url)

# Use Result pattern for explicit success/failure
try:
    return Result.success(data)
except Exception:
    return Result.failure(exc)
```

## State Machine
- **CLOSED** — normal operation, failures counted
- **OPEN** — circuit tripped, calls fail fast (after `recovery_timeout`)
- **HALF_OPEN** — probe call to test recovery

## Key Features
- **`@circuit_breaker` decorator** — sync and async functions
- **`Result.success(value)` / `Result.failure(exc)`** — explicit outcome pattern
- **Manual overrides** — `force_open()` / `force_close()`
- **Configurable** — `failure_threshold`, `recovery_timeout`, `half_open_max_calls`

## When to Use
- Multi-step agent workflows calling external APIs
- Any call chain where one failure should fail fast and prevent cascading calls
- Bounded concurrency + circuit breaking = resilient parallel tool execution

## Last Verified: 2026-07-26
- Repo: tiny-circuit (created 2026-07-26)
- Status: Initial commit, no starred activity
