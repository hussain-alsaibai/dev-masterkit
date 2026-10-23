# README Claims Must Be Runnable — Every Snippet, Verified by Run

**A checklist for any README, guide, or doc snippet that shows an import or
an API call.**

On 2026-10-23 the `fast-cache` README advertised four APIs that **did not
exist in the code**: `swr_ttl=`, `@fc.cache`, `namespace=`, and a
`RedisBackend` adapter. All four raised `TypeError`. They had been
documented since 2026-08-16 — nearly two months of readers copying broken
snippets.

The same README's benchmark table cited numbers for "Apple M3, Python 3.12"
that were never measured on any machine, and its Quick Start referenced undefined
variables (`llm`, `prompt`, `text`, `embedding_model`).

> Found 2026-10-23 while shipping fast-cache v0.8.0. All snippets in this
> guide were executed before being written down. **Last verified:** 2026-10-23

## The Failure Modes

### 1. The advertised API does not exist

```python
# README claimed:
from fast_cache import cache
@cache(ttl=60, maxsize=1024)
def expensive_query(user_id: int) -> dict: ...

# Reality (v0.8.0, verified by dir()):
__all__ = ["Cache", "CacheStats"]      # no module-level `cache`
Cache(maxsize=None, ttl=None, maxmemory=None, evict_callback=None, thread_safe=True)
# -> ImportError: cannot import name 'cache' from 'fast_cache'
```

### 2. The benchmark table is fabricated

A table that cites a hardware platform and a Python version nobody ran is the
most damaging kind of documentation defect, because the specificity is what
makes it believable.

### 3. The snippet does not run standalone

Referencing `llm`, `prompt`, `text`, or `embedding_model` without defining
them means the reader cannot paste and run. A snippet that cannot be executed
is a description, not a snippet.

### 4. The docs describe a different version than the code

The `fast-cache` guide claimed `add()`, `touch()`, `update()`, `peek()`, and a
module-level `cache` object. The v0.8.0 `Cache` class has **none** of those
(`dir(Cache)` verified 2026-10-23):

```
cleanup, clear, delete, expire, get, get_or_set, has, info, items, keys,
load, mdelete, memory_usage, mget, mset, pop, save, set, size, stats,
ttl_remaining, values
```

The guide was written against a **different clone** of the repo (a v0.7.2
lineage with 102 passing tests and an async surface), not the v0.8.0 code.

## Procedure

1. **Extract every import and every symbol used.** Not by reading — by
   parsing the snippet.
2. **Resolve the symbol against the real module.** The most reliable check is
   an import, not a grep:

   ```python
   import importlib, inspect
   m = importlib.import_module("fast_cache")
   print(hasattr(m, "cache"))          # False
   print(inspect.signature(m.Cache.__init__))
   print([x for x in dir(m.Cache) if not x.startswith("_")])
   ```

   A `grep` for `class Cache` will not tell you the constructor signature; a
   `grep` for `def add` will not tell you whether the method is on the class
   or on a module-level function.

3. **Run the snippet.** Literally execute it. `python3 -c "..."` against the
   installed/checked-out package, from **outside** the source directory when
   packaging is in question.
4. **Grep the source for the version.** Confirm the guide's claimed version
   matches `pyproject.toml` and the code. If a repo has multiple local clones
   at different versions, say which one was verified.
5. **Reproduce every number.** Benchmark tables need a script. Ship
   `benchmark_swr.py` so the README can be regenerated from a run.
6. **Stamp the verification.** `**Last verified:** YYYY-MM-DD` plus the version
   and the test count, so the next reader knows how stale it is.

## The Version-Pinning Trap

There are three `fast-cache` clones on this machine:

| Path | Version | Tests |
|------|---------|-------|
| `workspace/fast-cache/` | v0.7.2 lineage (async, `add`/`peek`) | 102 passing |
| `workspace/repos/fast-cache/` | v0.8.0 (SWR, namespacing) | 54 passing |
| `github/fast-cache/` | v0.4.0 lineage | 78 passing |

A guide written from the first and published as if it described the second
is wrong in every snippet. **Always state which path was verified.**

## The Upstream Drift Problem

Docs also drift from the **published** package, not just the local tree.
Upstream `fast-cache` `pyproject.toml` still says `version = "0.3.0"` and its
`fast_cache.py` still carries the v0.8.0 deadlock. Anyone reading the upstream
README today gets the old, broken API.

So a verified guide must state three separate facts:

- what the **local** code does (verified by run),
- what the **upstream** published code does (checked by HTTP/raw fetch),
- that they differ.

## The Transferable Lesson

> **README accuracy is a growth lever, not housekeeping.** For a small
> library, the README is the only asset that carries trust. A fabricated
> benchmark table destroys that asset — not just the numbers, but the reason
> to believe any other number in the file.
>
> The cheapest defence is to make documentation **executable**: every
> snippet in a guide should be a snippet someone actually ran, and the guide
> should say which commit, which path, and which date it was run against.

See also `prompts/fail-closed-on-unavailable-data.md` for the sibling lesson
(absence of data is not a pass) and
`prompts/reentrant-lock-discipline.md` for the deadlock class that a
never-executed snippet would have caught.
