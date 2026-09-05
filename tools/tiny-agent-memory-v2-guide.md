# tiny-agent-memory-v2 — Tiered Agent Memory (v2)

**Source:** [hussain-alsaibai/tiny-agent-memory-v2](https://github.com/hussain-alsaibai/tiny-agent-memory-v2)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-09-05

> Three-tier memory architecture for AI agents. Working (~0ms) → Episodic (~1ms) → Semantic (~5ms). Zero dependencies. ~550 lines.

## When to use

- Agents that need memory at different timescales (current task, recent history, long-term knowledge)
- Autonomous agents that must survive restarts and recall past actions
- Upgrade path from `tiny-agent-memory` (v1) when you need working + episodic + semantic unified
- Lightweight alternative to Mem0, LangChain Memory, or recall.ai

## Quick Start

```python
from tiny_agent_memory import TieredMemory

mem = TieredMemory(agent_id="devin-1")

# Working memory — zero latency
mem.working["task"] = "Fix auth bug in login.py"
mem.working["error"] = "KeyError: 'token'"

# Episodic — what happened
mem.remember("Reviewed auth.py, found token not persisted in session storage")
mem.remember("Applied fix, tests pass", outcome="success", tags=["auth", "fix"])

# Semantic — what I know
mem.store("The auth module uses JWT tokens stored in request.headers")
mem.store("The session store is Redis at localhost:6379", source="config")

# Unified recall — searches all three tiers
results = mem.recall("auth token session")
print(results["episodes"])  # Recent episodes about auth
print(results["facts"])     # Known facts about auth
```

## Architecture

| Tier | Latency | Contents | Persistence | No-Deps Mode |
|------|---------|----------|-------------|--------------|
| **Working** | ~0ms | Current task, scratchpad | In-memory | ✅ |
| **Episodic** | ~1ms | What happened, compressed history | snapdb or in-memory | ✅ |
| **Semantic** | ~5ms | What I know, TF-IDF indexed | JSONL | ✅ |

Optional dep: `snapdb` for persistent episode storage — falls back to in-memory list if unavailable.

## CLI

```bash
# Record an episode
python -m tiny_agent_memory remember --agent-id my-agent "Fixed the null pointer"

# Recall from memory
python -m tiny_agent_memory recall --agent-id my-agent "null pointer"

# Show statistics
python -m tiny_agent_memory stats --agent-id my-agent

# Export full memory
python -m tiny_agent_memory export --agent-id my-agent --output memory.json
```

## Install

```bash
pip install tiny-agent-memory
```

Or copy the single file:
```bash
curl -O https://raw.githubusercontent.com/hussain-alsaibai/tiny-agent-memory-v2/main/tiny_agent_memory/tiered_memory.py
```

## Benchmarks

| Operation | Latency |
|-----------|---------|
| Working memory read/write | ~0.01ms |
| Episode recall | ~1ms |
| Semantic recall (100 facts) | ~5ms |
| Full snapshot | ~0.5ms |

## Integration

Pairs with `tiny-bounty-workflow` for memory persistence across bounty iterations, and `tiny-workflow-engine` for orchestration pipelines.

## See Also

- [tiny-agent-memory Guide](tiny-agent-memory-guide.md) — v1 (BM25/TF-IDF single-store)
- [tiny-memo Guide](tiny-memo-guide.md) — pub/sub event bus for agent inter-process communication
