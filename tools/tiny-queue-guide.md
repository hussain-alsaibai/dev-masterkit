# tiny-queue — Zero-Dependency Persistent Job Queue

## Repo
https://github.com/hussain-alsaibai/tiny-queue

## One-liner
Append-only NDJSON job queue with cross-process flock, exponential backoff, dead-letter handling, and crash recovery. Celery-in-one-file.

## Install
```bash
pip install tiny-queue
```

## Quick Example

```python
from tiny_queue import Queue, Worker

q = Queue("./jobs", cross_process_lock=True)
q.enqueue("send_email", {"to": "user@example.com"}, job_id="email-42")

def handler(payload, job_id):
    send_email(**payload)

Worker(q, handler).run()
```

## File layout

```
jobs/
├── pending.jsonl     # awaiting execution
├── inflight.jsonl    # currently held by a worker
└── dead.jsonl        # exceeded max_retries → do not retry
```

## Properties

| Property | How |
|----------|-----|
| Append-only | NDJSON; one record per line |
| Atomic writes | `os.replace` + optional `fsync` |
| Cross-process safety | `fcntl.flock` (toggleable — see Gotcha) |
| Exponential backoff | `backoff_base=2, backoff_jitter=0.3` |
| Idempotency | Caller-supplied `job_id`; replays are deduped |
| Crash recovery | `reap_stale(older_than_seconds=300)` on startup |

## Worker

```python
from tiny_queue import Worker

w = Worker(
    queue=q,
    handler=send_email,
    max_retries=5,          # → dead.jsonl after 5 failures
    poll_interval=1.0,
)

w.run()                     # blocking
# or
w.run_once()                # single pass; useful in tests
```

## Disabling flock for Docker tmpfs

```python
q = Queue("./jobs", cross_process_lock=False)

# Or via env var:
#   TINY_QUEUE_NO_FLOCK=1
```

## Testing

- **29/29 tests passing**
- 6 test categories (basic enqueue/dequeue, backoff math, idempotency,
  crash recovery, dead-letter, flock toggle)
- 0 dependencies, 0 transitive deps
- 1 file

## Gotcha — `fcntl.flock` is unreliable on tmpfs in Docker

If you run tests in a tmpfs-backed container, a `Queue("./jobs")` inside
a test may hang indefinitely on `test_purge_clears_all`.
Root cause: even within the same process, `flock` on a tmpfs file can
block forever if some intermediate library acquires its own lock.

**Fix paths (any one is enough):**
1. Construct with `cross_process_lock=False`.
2. Set env `TINY_QUEUE_NO_FLOCK=1`.
3. In CI: `pytest --basetemp=/var/tmp` (real fs).

This is also why the constructor parameter exists in the first place:
filesystem-dependent features should always be toggleable.

## Gotcha — naming collisions can recurse forever

Don't name an inner helper class the same as a method on the enclosing
class. A `class _process_lock` inside `class Queue` makes
`Queue._process_lock(self)` resolve to the method, not the class, and you
get infinite recursion on first use. Use `_ProcessLock` (capitalized) or a
distinct attribute name.

Last verified: 2026-07-03
