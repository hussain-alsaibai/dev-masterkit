# tiny-mem Guide

**Repo:** [hussain-alsaibai/tiny-mem](https://github.com/hussain-alsaibai/tiny-mem)  
**Size:** ~480 LOC (src/) | **Deps:** 0, NumPy optional | **Last verified:** 2026-07-24

> Local-first memory for AI agents. Zero dependencies. JSON, vector, or hybrid backends.

## What it does

A local-first agent memory system with three backends (JSON, Vector, Hybrid). Supports semantic search, per-user/session scoping, time-aware recall, and pluggable embedding functions. Persists to SQLite with WAL mode.

## When to use

- **Agent memory** — store and retrieve facts, context, conversation history
- **RAG systems** — local knowledge retrieval without external vector DBs
- **Per-user memory isolation** — scoped stores for multi-tenant applications
- **Offline-first apps** — no external dependencies, works completely locally

## Key patterns

```python
from tiny_mem import HybridMemory, OpenAIEmbedder

mem = HybridMemory(
    embedder=OpenAIEmbedder(),
    persist_path="agent_memory.db"
)
mem.add("Alice prefers concise responses", importance=5, session="support-001")
results = mem.search("What does Alice prefer?", top_k=3)
```

## Notes

- NumPy is optional — auto-falls-back to pure-Python cosine similarity
- Supports hash-based "no-model-needed" embedder for fully offline use
- MIT licensed, pyproject.toml ready, not yet on PyPI

## Related

- `tiny-agent` — agent framework that can use tiny-mem as its memory backend
- `tiny-memory` — BM25+TF-IDF alternative with different similarity approach
- `tiny-embed` — compatible embedding functions for use with tiny-mem
