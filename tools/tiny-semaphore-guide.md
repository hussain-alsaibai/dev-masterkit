# tiny-semaphore — Async Semaphore with Timeout + Fairness

## Repo
https://github.com/hussain-alsaibai/tiny-semaphore

## One-liner
Zero-dep async semaphore with timeout and FIFO fairness. Bounded concurrency for parallel tool calls.

## Install
```bash
pip install tiny-semaphore
```

## Quick Example
```python
from tiny_semaphore import AsyncSemaphore

sem = AsyncSemaphore(limit=3)  # max 3 concurrent

async with sem.acquire():
    await do_work()
```

## Key Features
- **`AsyncSemaphore(limit, fairness=False)`** — acquire() as context manager
- **`acquire_gather(tasks, timeout)`** — run N tasks with bounded concurrency
- **Fairness (FIFO)** — waiting tasks are granted in order of arrival
- **Stats** — `active`, `waiters`, `timeouts` counters
- **Timeout** — `acquire(timeout=30)` raises if not granted in time
- Zero dependencies, stdlib only, fully type-hinted

## Bounded Parallelism Pattern
```python
from tiny_semaphore import AsyncSemaphore

async def run_batch(items: list[str]) -> list[Result]:
    sem = AsyncSemaphore(limit=5)
    tasks = [sem.acquire_gather([process(item)], timeout=60) for item in items]
    results = await asyncio.gather(*tasks)
    return [r for sublist in results for r in sublist]
```

## Last Verified: 2026-07-26
- Repo: tiny-semaphore (created 2026-07-26)
- Status: Initial commit, no starred activity
