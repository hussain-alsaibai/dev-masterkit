# tiny-agent-memory — Agent Memory System

**Source:** [hussain-alsaibai/tiny-agent-memory](https://github.com/hussain-alsaibai/tiny-agent-memory)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-10-24

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

## API & CI Correction (2026-10-24)

**50 tests passing** (verified by run, 2026-10-24). Version `0.1.0` in both
`pyproject.toml` and `__version__` - they match.

Two CI defects were fixed on 2026-10-24:

- **The workflow file was unparseable.** `continue_on_error` is not a GitHub
  Actions key; the real key is `continue-on-error`. GitHub rejected the whole
  file, so **the job never ran** - the badge was red for a parse error, not
  for any behaviour. Fixed, and all 44 of our workflow files now validate
  against the official Actions JSON Schema.
- **`testpaths` pointed at a file that did not exist.** The config named a
  test module the repo did not have, so pytest collected zero items while the
  workflow reported success.

This is the same lesson as `prompts/ci-target-must-match-repo-layout.md`:
**a green badge and a version number are both claims**, and neither is
detectable without reading the CI target and the two version fields side by
side.

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
