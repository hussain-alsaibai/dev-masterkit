# tiny-store Tool Guide

> Filesystem-backed key-value store with TTL, search, pagination, and watch. Zero dependencies. Atomic writes, crash-safe.

**Source:** [hussain-alsaibai/tiny-store](https://github.com/hussain-alsaibai/tiny-store)
**License:** MIT | **Language:** Python | **Last verified:** 2026-07-31

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
from tiny_store import TieredStore
from fast_cache import LRUCache

tiered = TieredStore(
    l1=LRUCache(capacity=1000),
    l2=Store("./data")
)
```

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

## Ecosystem Context

Part of the **tiny-*** zero-dependency Python ecosystem. Best paired with `fast-cache` for L1+L2 tiering (memory + disk).

## See Also

- [fast-cache guide](fast-cache-guide.md) — L1 in-memory cache
- [tiny-memory](tiny-memory-guide.md) — semantic agent memory
