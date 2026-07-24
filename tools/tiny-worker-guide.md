# tiny-worker — Zero-Dependency Background Worker

## Repo
https://github.com/hussain-alsaibai/tiny-worker

## What It Does

Zero-dependency background worker for Python. Like a lightweight Celery or RQ — submit jobs, workers pick them up, results stored in a file or SQLite.

## When to Use

- Background job processing without Redis/Celery overhead
- Simple async task queues for agents and scrapers
- Cron replacement for periodic background tasks

## Key Features

- Pure stdlib: `threading`, `queue`, `sqlite3`, `json`
- Submit jobs via function call or CLI
- Persistent job queue survives restarts
- Result storage with TTL expiry
- Retry support with backoff
- Dead-letter queue for failed jobs

## Quick Start

```python
from tiny_worker import Worker, job

@job
def process(item):
    return item * 2

# Submit
result = process.submit([1, 2, 3])  # returns job_id
print(process.get_result(result.job_id))  # [2, 4, 6]

# Worker
worker = Worker(queue="default")
worker.run()  # blocks, processes jobs
```

## Last Verified
2026-07-23
