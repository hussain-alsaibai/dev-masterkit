# tiny-worker Guide

## Repo
https://github.com/hussain-alsaibai/tiny-worker

## What It Does

Zero-dependendency background task worker for Python. One file, no setup.
Thread-pool worker with retries, rate limiting, and task objects.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_worker import Worker,
job` — the `job` decorator does not exist in the shipped module.
Verified against upstream `tiny_worker.py`:

```
__all__ = ['Worker', 'Task', 'RetryPolicy', 'RateLimiter']
```

Top-level names: `Worker`, `Task`, `RetryPolicy`, `RateLimiter`, and a
**`task`** function (singular, not `job`).

## Key Features

- `Worker` — runs submitted tasks on a thread pool
- `Task` — a unit of work with args/kwargs
- `RetryPolicy` — retry configuration
- `RateLimiter` — built-in throttle for task submission

## Quick Start

```python
from tiny_worker import Worker, task

worker = Worker(max_workers=4)

@task(retries=3)
def send_email(to: str, body: str) -> None:
    ...

worker.submit(send_email, to="a@example.com", body="hi")
worker.join()
```

## When to Use

- Running background work from an agent or a CLI without Celery
- Needing retries with a policy, per-job rate limiting, and a single-file
  dependency-free implementation
- Jobs that must finish before the process exits (`worker.join()`)

## Related

- `tools/tiny-queue-guide.md` — durable job queue (JSONL, DLQ) when jobs must survive a restart
- `tools/tiny-task-guide.md` — `tiny-task`, a different repo with a `TaskStore`
