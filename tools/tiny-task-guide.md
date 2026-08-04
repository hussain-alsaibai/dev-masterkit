# tiny-task — Durable Task Queue

**Created:** 2026-08-04
**Last verified:** 2026-08-04
**Author:** OpenClaw / hussain-alsaibai
**Repo:** https://github.com/hussain-alsaibai/tiny-task
**License:** MIT | **LOC:** ~350 | **Tests:** 11 passing | **Deps:** 0

## What It Does

Zero-dependency durable task queue with priority, TTL, retries, multi-worker support, and JSONL persistence.

## When to Use

- Background job execution for AI agents (bounty checks, report generation, batch ops)
- Durable task queues where Redis is overkill
- Multi-worker task distribution without a message broker

## Key Features

- Priority queue (lower = higher priority)
- TTL with auto-expire
- Configurable max retries with backoff
- Multi-worker support via polling
- JSONL persistence (one file per task)
- Task status: pending / running / done / failed / expired

## Quick Start

```python
from tiny_task import TaskStore, Worker, enqueue, get_task

store = TaskStore(".my-tasks/")
store.enqueue("math.fsum", [1, 2, 3], priority=10)
worker = Worker(store, handler={"math.fsum": lambda args: sum(args)})
worker.start()
task = get_task("abc123")
print(task.status, task.result, task.error)
```

## Integration

- **tiny-retry** — Wrap handlers with retry logic
- **tiny-circuit-breaker** — Bulkhead isolation
- **tiny-log** — Structured logging for task lifecycle
- **snapdb** — Persist aggregated results
