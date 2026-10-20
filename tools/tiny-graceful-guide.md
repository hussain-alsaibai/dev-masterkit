# tiny-graceful Guide

**tiny-graceful** — Zero-dependency cross-platform graceful shutdown for threaded and asyncio services. One shutdown signal, one global drain deadline, hooks fired in reverse registration order.

- **Repo:** github.com/hussain-alsaibai/tiny-graceful
- **Install:** `pip install tiny-graceful` or copy `tiny_graceful.py`
- **Size:** ~280 LOC, 0 dependencies
- **Tests:** 55 passing
- **Last verified:** 2026-10-20

## Why This Exists

GitHub's `graceful-shutdown` topic has several single-platform libraries (turnbullerin/graceful for Windows, grintor/win_graceful_shutdown, graceful-shutdown-py for asyncio) but no cross-platform importable answer that covers both `threading` and `asyncio` services and gives the caller one global drain budget to share between them. tiny-graceful fills that gap with stdlib-only code.

## Quick Start

```python
# Threaded service
from tiny_graceful import Shutdown, coordinator, serve

shutdown = Shutdown()

@shutdown.hook(priority=10)
def close_db():
    pool.close()

def worker(item):
    if shutdown.triggered:
        return
    process(item)

serve(workers=[worker] * 4, queue=q, shutdown=shutdown)

# Or: install signal handlers automatically
with coordinator(shutdown=shutdown):  # traps SIGINT/SIGTERM
    run_service()
```

```python
# Async service
from tiny_graceful import AsyncShutdown, async_serve

shutdown = AsyncShutdown()

@shutdown.hook
async def flush():
    await client.flush()

await async_serve(coros, shutdown=shutdown)
```

## Key Features

| API | Purpose |
|---|---|
| `Shutdown()` / `AsyncShutdown()` | One-shot trigger with idempotent `.trigger()` |
| `@shutdown.hook(priority=N)` | Register cleanup, fired in REVERSE priority order |
| `coordinator(period=0.5)` | Context manager; installs SIGINT/SIGTERM handlers |
| `serve(workers, queue, shutdown, drain_timeout=10.0)` | Worker pool + shutdown in one call |
| `async_serve(coros, shutdown, drain_timeout=10.0)` | Async equivalent |

## Rules (Invariants)

1. **Reverse registration order.** Hooks fire from last-registered to first-registered (LIFO). Enforced with a sorted list, not a heap, because hook count is small.
2. **Failing hooks never block the rest.** A hook that raises is logged and recorded; downstream hooks still run.
3. **One global drain budget.** The `drain_timeout` is shared across all hooks. If you need per-hook timeouts, budget them yourself.
4. **Idempotent trigger.** Calling `.trigger()` twice is a no-op; the second call returns the same `StopReason` (one of `SIGINT`, `SIGTERM`, `MANUAL`, `DEADLINE_EXCEEDED`, `EXHAUSTED`).
5. **Signal handlers only on main thread.** `serve()` and `async_serve()` trap SIGTERM/SIGINT themselves; for the context manager, you must be on the main thread (Python's signal semantics). Tests use a `shutdown=` parameter rather than raising a real signal, because real signals from helper threads cannot install handlers and would kill the test runner.

## Injection Pattern

Pass `shutdown=` into `serve()` / `async_serve()` so tests, admin endpoints, and the real signal path all converge on the same exit flow:

```python
shutdown = Shutdown()

# /admin/drain endpoint
@app.post("/admin/drain")
def drain():
    shutdown.trigger("MANUAL")
    return {"ok": True}

# Test
def test_drain():
    s = Shutdown()
    s.trigger("MANUAL")
    assert all_called(s)
```

## Verified End-to-End

```bash
$ timeout -s TERM python3 example.py
# StopReason.SIGTERM captured, hooks fired in exact reverse order,
# drain budget honored, no Thread.join hangs.
```

## When to Use

- Shutting down FastAPI / uvicorn cleanly so in-flight requests finish
- Draining a worker queue before the orchestrator (systemd, k8s preStop)
- Coordinating DB connection pools with background tasks
- Any service that needs SIGTERM to behave, not to be SIGKILL'd

## When NOT to Use

- Pure CLI scripts — use `signal.signal()` directly
- Long-running batch jobs with structured checkpoints — pair with `tiny-checkpoint` instead
- Service meshes where the platform owns shutdown (k8s with `terminationGracePeriodSeconds` and a real preStop hook)

