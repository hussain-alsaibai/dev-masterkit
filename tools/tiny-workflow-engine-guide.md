# tiny-workflow-engine Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-workflow-engine
**License:** MIT
**Last verified:** 2026-08-25

## What It Is

Zero-dependency async workflow engine with DAG execution, persistence, and retry. Single file (~500 LOC), pure stdlib (`asyncio`, `json`, `pathlib`).

## What It Does

- **DAG execution** — steps run in topological order; deps are enforced
- **Async + sync** — `async def` and regular `def` steps work seamlessly
- **Parallel fan-out** — run multiple steps concurrently; merge results downstream
- **Persistence** — checkpoint every step to JSON; resume from last checkpoint on crash
- **Retry + backoff** — exponential backoff per step; configurable attempt count
- **Timeout** — per-step timeouts with `asyncio.wait_for`
- **Hooks** — `on_start`, `on_step_start`, `on_step_complete`, `on_step_fail`, `on_complete`, `on_fail`
- **Map** — fan a callback out over a list of items concurrently
- **Zero deps** — pure Python stdlib

## When to Use It

- AI agent pipelines (fetch → generate → store workflow)
- Multi-step data processing with crash resilience
- Replacing Celery/Temporal for simple cases where those are overkill
- Durable orchestration that survives process restarts

## Quick Example

```python
from tiny_workflow_engine import WorkflowEngine

engine = WorkflowEngine(persist_dir="./workflows/")

wf = engine.create("my-pipeline")
wf.add_step("fetch", fetch_data)
wf.add_step("process", process_data, deps=["fetch"])
wf.add_step("save", save_results, deps=["process"])

result = await engine.run("my-pipeline")
# result = {"fetch": ..., "process": ..., "save": ...}
```

## Resume After Crash

Fix the bug, redeclare the same DAG, and run again: completed steps are skipped, failed step retries fresh. Checkpoint persists after every step.

## Related

- [tiny-event-bus](tools/tiny-event-bus-guide.md) — pub/sub for cross-component events
- [tiny-workflow-guide](tools/tiny-workflow-guide.md) — older workflow guide (different repo)
