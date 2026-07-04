# tiny-timeout — Zero-Dependency Timeouts

## Repo
https://github.com/hussain-alsaibai/tiny-timeout

## One-liner
Timeouts that work on every thread and OS — hard cut-offs via worker thread, cooperative deadlines, and decorator wrappers. No `signal.alarm` (which only works on the main thread), no `asyncio.wait_for` (which only works in event loops).

## Install
```bash
pip install tiny-timeout
```

## Three APIs

### 1. `run_with_timeout(func, seconds, default=...)` — hard cut-off

```python
from tiny_timeout import run_with_timeout, TimeoutExceeded

result = run_with_timeout(slow_call, seconds=5, default=None)
if result is None:
    log.warning("call timed out, used default")
```

The function runs in a worker thread. If it doesn't return in `seconds`, the
thread is *abandoned* (it will die when the process dies; the call returns
`default`). The wait is cut off cleanly.

### 2. `@timeout(seconds)` — decorator

```python
from tiny_timeout import timeout

@timeout(30)
def fetch_user(user_id):
    return db.query("SELECT * FROM users WHERE id = ?", user_id)
```

Equivalent to wrapping every call in `run_with_timeout`.

### 3. `with timeout(seconds) as d:` — cooperative deadline

```python
from tiny_timeout import timeout, Deadline

with timeout(5) as d:
    for item in huge_list:
        if d.expired():
            break
        process(item)
```

Inside the block, `d` is a `Deadline` you can poll, compare, or use to cap
loops. Use `Deadline.from_seconds(s)` for an explicit deadline handle:

```python
d = Deadline.from_seconds(10)
while not d.expired():
    item = queue.get(timeout=d.remaining())
    process(item)
```

## Capped sleep

```python
from tiny_timeout import sleep_with_deadline, Deadline

d = Deadline.from_seconds(60)
while not d.expired():
    sleep_with_deadline(5, d)   # wakes at most every 5s, but no later than d
    poll()
```

## Exception

```python
from tiny_timeout import TimeoutExceeded

try:
    run_with_timeout(risky_call, seconds=2)
except TimeoutExceeded as e:
    print(f"timed out after {e.elapsed:.2f}s (asked for {e.seconds}s)")
```

`TimeoutExceeded` is *only* raised when `default` is the sentinel
`UNSET`. Otherwise the call returns `default`.

## Why this library exists

- `signal.alarm(seconds)` — only works on the **main thread**; useless in workers
- `asyncio.wait_for(...)` — only works inside an **event loop**; useless in sync code
- `threading.Timer` — fires a callback but doesn't unblock the wait
- `concurrent.futures.wait_for(...)` — works, but doesn't expose `Deadline`

`tiny-timeout` covers all four cases with one mental model.

## Properties

| Property | How |
|----------|-----|
| Hard cut-off | `Future.result(timeout=…)` against a worker thread |
| Cooperative | `Deadline.expired()` / `Deadline.remaining()` |
| Cross-thread | Worker thread for hard, polling for cooperative |
| Cross-platform | Linux / macOS / Windows |
| Async-safe | `deadline` is just a float, works in any code path |

## Testing

- **21/21 tests passing**
- 6 test categories (hard cut-off, decorator, context manager, deadline
  arithmetic, sleep cap, exception attributes)
- 0 dependencies, 0 transitive deps
- 1 file
- ~500 LOC

## Gotcha — the worker thread is NOT cancelled

`Future.result(timeout=N)` cuts off the wait but the worker keeps running.
The thread is a daemon in a shared `ThreadPoolExecutor`, so it dies with the
process — but it consumes CPU and holds whatever resources the function
grabbed until it returns naturally.

**Mitigations:**
1. Don't run *expensive* work inside `run_with_timeout` for long; the thread
   outlives the timeout.
2. If the work is expensive and you can interrupt it, pass a `threading.Event`
   to the function and check it periodically.
3. For a hard kill, use `multiprocessing` + `Process.terminate()` — but that's
   a different library.

Document this honestly. Don't pretend the thread is killed when it isn't.

## Gotcha — `concurrent.futures.TimeoutError` is not `TimeoutError`

The stdlib has *two* `TimeoutError` classes:
- The builtin `TimeoutError` (a subclass of `OSError`)
- `concurrent.futures.TimeoutError` (a different exception)

`run_with_timeout` raises our own `TimeoutExceeded`. When aliasing stdlib
names, prefer explicit suffixes:

```python
# bad: shadowing builtin
from concurrent.futures import TimeoutError as TimeoutError

# good: explicit suffix
from concurrent.futures import TimeoutError as CFTimeoutError
```

## Related ecosystem

- **`tiny-rate`** — token bucket can use `Deadline` for fixed-window reset
- **`tiny-retry`** — backoff needs `deadline.remaining()` to bound total time
- **`tiny-pool`** — workers should respect `Deadline` for graceful shutdown
- **`tiny-queue`** — `reap_stale(older_than_seconds=...)` uses a deadline internally

Last verified: 2026-07-04