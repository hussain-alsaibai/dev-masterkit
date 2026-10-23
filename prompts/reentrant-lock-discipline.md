# Reentrant Lock Discipline — A Plain Lock Is Not Reentrant

**A checklist for any code that holds a lock and calls back into code that
also takes that lock.**

Two separate repos shipped the same defect in two days: `fast-cache` v0.8.0
(`Cache.info()`) and `tiny-mcp-registry` (`export()`). Both deadlocked
*permanently*, with no error, no timeout, and no traceback.

> Found 2026-10-23 on `fast-cache` v0.8.0. The legacy test suite also hung:
> `test_info` never returned. The suite printed all dots and then stopped.
> **Last verified:** 2026-10-23

## The Failure Mode

`threading.Lock` is **not reentrant**. If a thread already holds the lock and
tries to acquire it again, it blocks forever. The canonical shape:

```python
# BROKEN — to_dict() holds the lock, then calls hit_rate() which re-takes it
class CacheStats:
    def __init__(self):
        self._lock = threading.Lock()

    def hit_rate(self) -> float:
        with self._lock:          # <-- second acquisition
            total = self.hits + self.misses
            return self.hits / total if total else 0.0

    def to_dict(self) -> dict:
        with self._lock:          # <-- first acquisition, still held
            total = self.hits + self.misses
            hit_rate = self.hit_rate()   # <-- DEADLOCK
            return {...}
```

There is no exception. There is no timeout. There is no log line. The thread
simply stops. If it is the main thread, the process appears to hang; if it is a
worker thread, the pool slowly loses workers and throughput decays to zero.

## Why It Hides So Well

- The locking code **looks correct**. Each method acquires the lock exactly
  once, in isolation.
- The bug only appears when one locked method calls another locked method.
- Unit tests that exercise the methods *separately* all pass.
- The failure is a hang, not a wrong answer, so no assertion catches it.

## Detection: The Symptom to Watch For

> **The test suite prints all dots and then hangs forever at exit.**

That is the signature. If a suite shows 100% dots and never prints the summary
line, suspect a lock. Add a timeout to the run:

```bash
timeout 30 python -m pytest -q -x   # 30s cap
```

A hang that disappears when the suite is run with `-p no:cacheprovider` or
when one test is skipped is a strong lock signal.

## The Fix — Three Rules

### Rule 1: Use `RLock` when a lock may nest

```python
self._lock = threading.RLock()   # reentrant: same thread may re-acquire
```

`RLock` is a drop-in replacement for `Lock` in nearly every case. The cost is
small; the failure mode it removes is permanent.

**When to use `RLock`:** any lock whose protected code calls another method on
the same object that also takes the lock. If you are unsure, use `RLock`.

### Rule 2: Snapshot under the lock, build the payload outside it

The cleanest pattern — it removes the nesting entirely rather than tolerating
it:

```python
def to_dict(self) -> dict:
    with self._lock:
        hits, misses = self.hits, self.misses   # snapshot
    total = hits + misses
    return {"hits": hits, "misses": misses,
            "hit_rate": round(hits / total, 4) if total else 0.0}
```

Reading counters under one acquisition and computing derived values outside it
makes the reentrancy question moot.

### Rule 3: Never let a lock guard a call into caller-supplied code

If a locked method invokes a callback, a factory, a handler, or anything that
might re-enter the object, the lock is held across unknown code. Either:

- copy what you need under the lock, release it, then call out; or
- pass the lock's own reentrancy guarantee (`RLock`) and document it.

## Procedure

1. **Grep for the pattern.** `grep -rn 'threading.Lock()' src/` then read every
   locked method for calls to sibling methods.
2. **Look for the nested call.** A locked method calling `self.<other_method>`
   where that method also takes `self._lock` is a deadlock.
3. **Check the lock type.** `Lock()` where nesting is possible -> `RLock()`.
4. **Bound the test run.** `timeout 30 python -m pytest -q`. A suite that
   prints all dots and never finishes has found it.
5. **Prove the fix.** Revert the fix in a scratch copy and confirm the suite
   hangs again. A test that passes both before and after the fix proves
   nothing.

## The Family-Wide Pattern

This is the third instance of a broader family in the tiny-* ecosystem. The
previous two were:

| Repo | Method | Symptom |
|------|--------|---------|
| fast-cache v0.7.1 | CRDT merge slot | Slot not freed on exception |
| tiny-mcp-registry | `export()` | Held lock, called `stats()` |
| fast-cache v0.8.0 | `Cache.info()` | Held lock, called `hit_rate()` |

Two of those three are **non-reentrant lock** defects, and the third is
**"fail fast, free the slot"**. The shared shape: a shared resource is
protected by a lock, and the protected code reaches back into the same
resource.

## The Transferable Lesson

> **A deadlock is a correctness bug with no symptom.** There is no exception
> to catch and no log line to read. The only evidence is that time stopped.
> Any code path that holds a lock across a call it does not control needs a
> bounded test to prove it returns.
>
> The cheap structural defence is boring and always right: use `RLock` when
> nesting is possible, and snapshot under the lock rather than computing
> inside it.
