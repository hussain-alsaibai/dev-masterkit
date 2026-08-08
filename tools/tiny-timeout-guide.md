# tiny-timeout — Hard Timeouts

## Summary

Zero-dependency hard timeout enforcement. Kills runaway operations that block or loop forever. Uses multiprocessing + SIGKILL — not Thread.join() which is unreliable.

## Quick Reference

- **Repo:** [hussain-alsaibai/tiny-timeout](https://github.com/hussain-alsaibai/tiny-timeout)
- **Lines of code:** ~200
- **Tests:** 14 (all passing)
- **Dependencies:** None (stdlib only)

## Usage

### `timeout(seconds)` decorator

```python
from tiny_timeout import timeout

@timeout(5.0)
def slow_operation():
    # Raises TimeoutError if runs > 5 seconds
    import time; time.sleep(10)
```

### `run_with_timeout(func, seconds, *args, **kwargs)`

```python
from tiny_timeout import run_with_timeout

result = run_with_timeout(heavy_function, 3.0, arg1, arg2)
# Returns (True, value) on success, (False, TimeoutError) on timeout
```

### `TimeoutTracker`

```python
from tiny_timeout import TimeoutTracker

tracker = TimeoutTracker(max_concurrent=10)
future = tracker.submit(slow_task, timeout=5.0)
result = future.result()  # raises TimeoutError if exceeded
```

## Key Design

- Uses `multiprocessing.Process` + `SIGKILL` — cannot be caught or suppressed
- Unlike `threading.Timer`, this actually terminates blocking I/O and infinite loops
- Does NOT work on Windows (SIGKILL is Unix-only)
- Graceful termination tries `SIGTERM` first, escalates to `SIGKILL` after grace period

## Last Verified

2026-08-08
