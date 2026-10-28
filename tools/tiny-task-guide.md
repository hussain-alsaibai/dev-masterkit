# tiny-task Guide

## Repo
https://github.com/hussain-alsaibai/tiny-task

## What It Does

Zero-dependency durable task queue for Python. One file, no setup. JSONL-backed,
with priority, TTL, retries, and multiple workers.

## Last Verified
2026-10-28 - **11 tests passing** (measured by run against the canonical
published clone at `/home/node/repos/tiny-task`). The package had **no CI**
until 2026-10-28.

## The Wheel Shipped Nothing (fixed 2026-10-28)

The wheel contained **no importable module**, because
`[tool.setuptools.packages.find]` with `include = ["tiny_task*"]` finds
nothing - a single top-level module is not a package. Fixed with
`[tool.setuptools] py-modules = ["tiny_task"]`.

**Two implementations of `tiny-task` exist** and this guide documents the
canonical one: the published v1.0.0 at `/home/node/repos/tiny-task` (11 tests)
and an unrelated v0.1.0 in the workspace. The canonical clone is the published
one and is what the CI fix was applied to.

## Previous verification
2026-10-23
## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_task import TaskStore,
Worker, enqueue`. Verified against upstream `tiny_task.py`:

```
Status, Task, _import_func, _encode, TaskStore, Worker, _default,
enqueue, get_task, list_tasks, cancel_task, task_stats
```

`TaskStore`, `Worker`, and `enqueue` **are** present upstream, so that part of
the guide was correct. The addition for 2026-10-23: the module-level
**`Status`** enum, plus `get_task`, `list_tasks`, `cancel_task`, and
`task_stats` for inspecting and cancelling queued work.

Note: the **local** clone at `workspace/tiny-task/` currently exposes only
`Task` and `TinyTask` — the full surface above is the upstream module. Verify
which clone you are importing from before relying on `TaskStore`.

## Quick Start

```python
from tiny_task import TaskStore, Worker, enqueue, Status

store = TaskStore("tasks.jsonl")
enqueue(store, "send_report", to="a@example.com", priority=5)

worker = Worker(store, concurrency=4)
worker.run()
```

## When to Use

- Jobs that must survive a process restart (JSONL on disk)
- Per-task priority, TTL, and retry policy
- A cron job or agent that needs a queue without Redis

## Related

- `tools/tiny-queue-guide.md` — `tiny-queue`, a different repo (NDJSON + dead-letter)
- `tools/tiny-worker-guide.md` — `tiny-worker`, in-memory worker without persistence
