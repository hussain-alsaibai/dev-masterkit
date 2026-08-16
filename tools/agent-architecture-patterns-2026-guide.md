# Tool Guide: agent-architecture-patterns-2026

> **Last verified:** 2026-08-16
> **Repo:** https://github.com/hussain-alsaibai/agent-architecture-patterns-2026
> **License:** MIT

## What it is

Technical field guide to the 7 architectural patterns that power production autonomous agents in 2026. Language-agnostic concepts with Python code examples (mostly `tiny-*` ecosystem). Markdown-based knowledge base.

## When to use

- Choosing an agent architecture for a new project
- Refactoring an existing agent system
- Evaluating patterns: ReAct vs DAG vs Fleet
- Learning production agent design patterns

## Quick reference

| # | Pattern | Use When |
|---|---------|----------|
| 1 | **ReAct Loop** | Simple single-agent tasks, well-defined tool sets |
| 2 | **Sub-Agent Dispatch** | Parallel work, task decomposition, isolation |
| 3 | **DAG Workflow** | Multi-step pipelines with dependencies, retries, human gates |
| 4 | **Streaming State Machine** | Interactive UIs, long responses, real-time dashboards |
| 5 | **Memory Tiering** | Long sessions, large codebases, persistent context |
| 6 | **Budget-Gated Autonomy** | Cost control, production deployments, multi-tenant |
| 7 | **Fleet Orchestration** | Multiple agents, work queues, priority routing |

## Related tools

- `tiny-agent` — ReAct loop implementation in one file
- `tiny-workflow` — DAG orchestrator with retry + approval gates
- `tiny-memory` — BM25 + TF-IDF agent memory
- `tiny-cost` — token cost tracking and budget enforcement
- `python-architect` skill — agent persona for architecture decisions
