# tiny-memory Guide

> Zero-dependency AI agent memory. BM25 + TF-IDF similarity. Three store types. JSONL persistence. No embeddings API, no vector DB.

**Repo:** https://github.com/hussain-alsaibai/tiny-memory
**Last Verified:** 2026-07-22

## Quick Start

```python
from tiny_memory import AgentMemory

mem = AgentMemory()
mem.remember("user_name", "Amara")
mem.memorize("User prefers Python and short answers.", metadata={"context": "preference"})
results = mem.query("What does the user prefer?", top_k=3)
```

## Three Stores

| Store | Purpose | API |
|-------|---------|-----|
| **SemanticMemory** | BM25 + TF-IDF cosine similarity, no embeddings API | `add()`, `search(query, hybrid=True)` |
| **EpisodicMemory** | LRU event log, JSONL persisted | `add(type, data)`, `get_recent(n)` |
| **DeclarativeMemory** | Key-value facts | `remember(k,v)`, `recall(k)`, `forget(k)` |

## When to Use

- **tiny-memory** → autonomous agents that need persistent, searchable context across sessions
- **tiny-embed** → when you have an embeddings API and want dense vector similarity
- **fast-cache** → simple TTL cache, not memory (no search)

## Integration

Agent memory pairs with tiny-chain for LLM calls and tiny-workflow for pipeline orchestration. Combine with tiny-router for callback receivers.

## See Also

- [tiny-chain Guide](tiny-chain-guide.md) — LLM processing
- [tiny-workflow Guide](tiny-workflow-guide.md) — DAG orchestration
- [tiny-agent](https://github.com/hussain-alsaibai/tiny-agent) — agent framework
