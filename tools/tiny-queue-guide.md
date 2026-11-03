# tiny-queue — Zero-Dependency Persistent Job Queue

## Repo
https://github.com/hussain-alsaibai/tiny-queue

## One-liner
Append-only NDJSON job queue with cross-process flock, exponential backoff, dead-letter handling, and crash recovery. Celery-in-one-file.

## Install

> **The PyPI name `tiny-queue` belongs to someone else** — the PyPI project
> `tiny-queue` (v0.1.0) is *"A modular, extensible Python queue service"*,
> a different project with no `hussain-alsaibai` project URL. **
> `pip install tiny-queue` succeeds and installs that package, not this one.**
> Verified live against the PyPI JSON API on 2026-11-03.
>
> This package is **not published to PyPI**. Install from the repository:

```bash
pip install git+https://github.com/hussain-alsaibai/tiny-queue.git
```

or copy `tiny_queue.py` into your project (single file, zero deps).

## Quick Example

```python
from tiny_queue import Queue, Worker

q = Queue("./jobs", cross_process_lock=True)
q.put({"to": "user@example.com"}, id="email-42")

def handler(job):
    send_email(**job.payload)

Worker(q, handler, poll_interval=0.5).tick()   # or .run_forever() to loop
```

**Executed on 2026-11-03** against the local clone. Real output:

```
size: 1
pending: ['email-42']
handler saw: [Job(id='email-42', payload={'to': 'user@example.com'}, status='inflight', ...)]
```

> **Corrections applied 2026-11-03.** The previous snippet called
> `q.enqueue("send_email", {...}, job_id="email-42")` and `Worker(...).run()`.
> **Neither method exists.** The API is `Queue.put(payload, *, delay=0.0,
> max_retries=None, id=None)` and the worker methods are `tick()` and
> `run_forever()`. The handler receives a **`Job` object**, not
> `(payload, job_id)`. The old snippet raised `AttributeError` on the first
> line.

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

**Last verified:** 2026-11-03 — upstream repo returns HTTP 200 (MIT, last push
2026-07-04); the PyPI name was probed live and found to belong to another
project; the snippet above was executed against the local clone.
