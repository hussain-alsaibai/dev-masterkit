# tiny-store Tool Guide

> Filesystem-backed key-value store with TTL, search, pagination, and watch. Zero dependencies. Atomic writes, crash-safe.

**Source:** [hussain-alsaibai/tiny-store](https://github.com/hussain-alsaibai/tiny-store)
**License:** MIT | **Language:** Python | **Last verified:** 2026-10-24

## When to use

- Persistent KV store when Redis is overkill
- L2 cache tier (L1 = fast-cache in memory, L2 = tiny-store on disk)
- Session storage, feature flags, job queues
- Need TTL, search, or file watching without a database
- Zero-dependency constraint

## Quick Start

```python
from tiny_store import Store

store = Store("./data", ttl=3600)  # 1h default TTL

# Basic get/set
store.set("user:42", {"name": "Amara", "plan": "pro"})
data = store.get("user:42")

# TTL
store.set("temp:key", value, ttl=60)  # expires in 60s

# Search
results = store.search(prefix="user:", regex=None)
results = store.search(regex="plan:.*pro")

# Pagination
for key, value in store.iterate(cursor=None, limit=50):
    print(key, value)

# Tiered L1 + L2
from tiny_store import TieredStore, Store

tiered = TieredStore(
    l1=Store("./l1"),
    l2=Store("./data")
)
```

> **Correction (2026-10-28):** this snippet previously imported `LRUCache`
> from `fast_cache`. **There is no `LRUCache` in `fast_cache`** - verified by
> import: it is absent from `dir(fast_cache)`. `fast_cache` exports `Cache`,
> `CacheAsync`, `CacheStats`, `DiskSpillover`, `CacheMetricsListener` and
> `cache_method`. `TieredStore` accepts any mapping-like object for `l1`,
> so a `fast_cache.Cache` works too - but the import in the snippet was wrong.

## Key Features

- **Atomic writes** — rename-after-write on POSIX
- **TTL support** — per-key or global with auto-expiry
- **WAL mode** — write-ahead log for durability
- **Search** — prefix scan, regex match, value filtering
- **Pagination** — cursor-based for large keyspaces
- **Watch** — file-system polling observer
- **JSONL import/export** — bulk operations
- **Tiered mode** — L1 memory + L2 disk composable

## Patterns

```python
# WAL for crash safety
store = Store("./data", wal=True)
store.set("job:1", {"status": "running"})
# Crash here → WAL replay recovers the write

# Key expiration check
if store.expired("session:abc"):
    store.delete("session:abc")
    return redirect("/login")

# Bulk export
store.export_jsonl("backup.jsonl")
store.import_jsonl("backup.jsonl")
```

## Verification (2026-10-26)

**24 tests passing** (verified by run 2026-10-26). Version `0.1.0` in both
`pyproject.toml` and `__version__` - they match. `ruff check` is clean.

The repo's CI workflow was unparseable until 2026-10-24 (`continue_on_error`
is not a GitHub Actions key - it is `continue-on-error`), so the job had never
run. Fixed and validated against the official Actions JSON Schema.

### The `TieredStore` falsy-dict bug (fixed 2026-10-26)

**A real library bug, found while fixing CI — not a CI defect.**

```python
# BROKEN - an empty dict is falsy, so the caller's dict was DISCARDED
self.hot = hot or {}

# CORRECT
self.hot = hot if hot is not None else {}
```

`TieredStore.__init__` replaced the caller's `hot` dict with a fresh one
whenever that dict was empty. Promoted keys were written into a dict nobody
could read. **The 21-test suite had zero `TieredStore` coverage**, which is
why it shipped.

Fixed, with 3 regression tests added (21 → 24).

> **A suite that does not cover the class you just changed cannot catch the
> bug you just changed.** Coverage is not a metric here; it is the answer to
> "would this test have failed before the fix?"

## Ecosystem Context

Part of the **tiny-*** zero-dependency Python ecosystem. Best paired with `fast-cache` for L1+L2 tiering (memory + disk).

## See Also

- [fast-cache guide](fast-cache-guide.md) — L1 in-memory cache
- [tiny-memory](tiny-memory-guide.md) — semantic agent memory
