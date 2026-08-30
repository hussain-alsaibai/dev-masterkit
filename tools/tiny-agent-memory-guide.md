# tiny-agent-memory — Agent Memory System

**Source:** [hussain-alsaibai/tiny-agent-memory](https://github.com/hussain-alsaibai/tiny-agent-memory)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-08-30

> Zero-dependency memory system for AI agents. Semantic + working + episodic memory in one file. No numpy required — but optional for faster vector search.

## When to use

- Autonomous agents that need persistent, searchable long-term context
- Agents running across sessions that must recall past actions
- Lightweight alternative to LangChain Memory, Mem0, or recall.ai
- When you want memory you can read, audit, and debug in an afternoon

## Quick Start

```python
from tiny_agent_memory import MemoryStore

store = MemoryStore(name="my-agent", persist_dir="/tmp/agent-memory")
store.add("user asked about the deploy pipeline", metadata={"type": "user_message"})
store.add("found the bug in config_loader.py line 47", metadata={"type": "agent_action"})
results = store.remember("deploy pipeline")
store.snapshot()
```

## Architecture

Three memory layers unified under one interface:

| Store | Purpose | Persistence | No-Deps Mode |
|-------|---------|-------------|--------------|
| **SemanticMemory** | Long-term recall via BM25/TF-IDF or numpy cosine similarity | JSONL | ✅ (BM25 only) |
| **WorkingMemory** | Short-term KV store for current session context | In-memory | ✅ |
| **EpisodicMemory** | LRU event log of past agent actions | JSONL | ✅ |

## Comparison vs Alternatives

| Solution | Dependencies | Lines | Cold Start |
|----------|-------------|-------|-----------|
| **tiny-agent-memory** | **None** (numpy optional) | **~400** | **Instant** |
| LangChain Memory | langchain + vectorstore + embeddings | 10K+ | Slow |
| Mem0 | OpenAI embeddings + Qdrant/Pinecone | 5K+ | Slow |
| recall.ai | Proprietary SDK | Closed | Slow |

## Integration

Pairs with [tiny-agent](https://github.com/hussain-alsaibai/tiny-agent) for the agent loop and [tiny-workflow-engine](https://github.com/hussain-alsaibai/tiny-workflow-engine) for orchestration pipelines.

## See Also

- [tiny-memory Guide](tiny-memory-guide.md) — older BM25/TF-IDF approach
- [tiny-agent Guide](tiny-agent-eval-guide.md) — agent evaluation harness
