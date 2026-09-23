# tiny-tool-cache — Stdlib-Only Tool / LLM Result Cache

**Repo:** https://github.com/hussain-alsaibai/tiny-tool-cache
**Install:** `pip install tiny-tool-cache` *(pending first push; copy `tiny_tool_cache.py` until then)*
**Last verified:** 2026-09-23
**Tests:** 33/33 in 0.055s

---

## What It Does

If you build autonomous agents you've hit *the* pattern:

```
agent: tool.kb_search("What is X?")
   → 800ms network call, expensive embed, returns [{...}, {...}]

agent (10 seconds later): tool.kb_search("What is X?")
   → 800ms network call, again
```

Three problems at once:

1. **Duplicate compute.** Same key, same answer.
2. **Stale-not-served.** When a 5-minute-old result still answers the question,
   agents should keep using it while a background refresh kicks off
   (stale-while-revalidate).
3. **Negative-result storms.** Agent asks → tool returns `[]` → agent retries
   → still `[]` → retry storm. The empty result is itself worth caching.

`tiny-tool-cache` solves those three.

It is **not**:

- a `redis` client (use `redis`),
- a process-shared cache (in-process only; for cross-process use shared memory),
- a `semantic` cache (use [`tiny-semantic-cache`](https://github.com/hussain-alsaibai/tiny-semantic-cache)),
- a `prompt → completion` cache (use [`tiny-prompt-cache`](https://github.com/hussain-alsaibai/tiny-prompt-cache)),
- a `memoize-pure-functions` library (use [`tiny-memo`](https://github.com/hussain-alsaibai/tiny-memo)).

## Install

```bash
# Copy one file
curl -O https://raw.githubusercontent.com/hussain-alsaibai/tiny-tool-cache/main/tiny_tool_cache.py

# or, once published:
pip install tiny-tool-cache
```

## Quickstart

### Decorator style (smallest)

```python
from tiny_tool_cache import ToolCache, NegativeCache

cache = ToolCache(
    ttl_seconds=300,
    max_entries=10_000,
    negative_cache=NegativeCache(ttl=60, is_empty=lambda v: not v),
)

@cache.wrap
def search_kb(query: str, limit: int = 10):
    return kb_client.search(query, limit=limit)
```

First call: runs `search_kb(...)`, caches the result. Calls within 300s
return cached. Calls after 300s trigger SWR — return the stale value
while recomputing in the background.

Async works the same: `@cache.awrap`.

### Manual style (more control)

```python
cache = ToolCache(ttl_seconds=300, max_entries=50_000)

user = cache.get_or_set(("users.find", 42), lambda: db.users.find(42))
```

### Crash-safe persistence

```python
cache = ToolCache(
    ttl_seconds=900,
    max_entries=20_000,
    persist_path="/var/tmp/tool-cache.jsonl",   # append-only JSONL
)
```

On startup, the file is replayed into memory (TTL-bounded). On every
`set`, a new line is appended with `fsync()` so a hard kill mid-flight
won't corrupt the cache — at worst, the last few writes are lost.

### Async coalescing

Two concurrent calls to the same key share **one** loader:

```python
import asyncio
from tiny_tool_cache import ToolCache

cache = ToolCache(ttl_seconds=60)

calls = []
async def fetch_one():
    calls.append(1)
    await asyncio.sleep(0.05)
    return "value"

async def runner():
    return await asyncio.gather(
        cache.aget_or_set("k", fetch_one),
        cache.aget_or_set("k", fetch_one),
    )

results = asyncio.run(runner())    # ONE loader call, two results
```

### Negative-result caching (stop empty-result retry storms)

```python
from tiny_tool_cache import ToolCache, NegativeCache

nc = NegativeCache(ttl=60, is_empty=lambda v: len(v) == 0)
cache = ToolCache(negative_cache=nc)

@cache.wrap
def list_open_tickets(since_minutes: int):
    return support.list_tickets(since=since_minutes)
```

When `support.list_tickets(...)` returns `[]`, that empty result is cached
for 60s (vs 5 minutes for non-empty results). Three retries during a
ticket storm collapse into one upstream call.

### Stats

```python
print(cache.stats.to_dict())
# {'hits': 487, 'misses': 21, 'hit_rate': 0.9586, 'stale_served': 4,
#  'negative_hits': 9, 'sets': 21, 'evictions': 0, 'expirations': 0,
#  'writes_to_disk': 21, 'loads_from_disk': 21}
```

## Tiny-* Family Siblings

- **`tiny-prompt-cache`** — caches LLM responses keyed by system prompt + prefix
- **`tiny-semantic-cache`** — semantic embedding similarity cache
- **`tiny-memo`** — memoize pure functions
- **`tiny-tool-cache`** — deterministic-key, bounded, TTL-aware, **agent-shape**
  (this repo)

This is the missing middle layer for agent tool/LLM call deduplication.

## When to use vs `fast-cache`

| Need | Use |
|------|-----|
| Pure-function memoization, microsecond perf | `fast-cache` (2.2M ops/sec, sync/async decorators) |
| Agent tool call result with TTL + SWR + negative cache + crash-safe persistence | `tiny-tool-cache` |
| Cross-process / distributed cache | `redis` |

They share a vibe (zero deps, stdlib only, single file, MIT) but `tiny-tool-cache`
is shaped for agent workloads (negative results, async coalescing, JSONL persistence),
while `fast-cache` is shaped for raw LRU throughput.
