# tiny-workflow Guide

> Async DAG orchestrator with retries, approval gates, dead-letter queue, and JSON state persistence. ~700 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-workflow
**Last Verified:** 2026-07-22

## Quick Start

```python
from tiny_workflow import Workflow, LambdaStep
import asyncio

async def fetch(ctx):
    return {"data": [1, 2, 3]}

def process(ctx):
    return {"total": sum(ctx["state"]["data"])}

wf = (
    Workflow()
    .step(LambdaStep("fetch", fetch))
    .step(LambdaStep("process", process, depends_on=["fetch"]))
    .run()
)
print(wf.state)
```

## Key Patterns

| Pattern | API |
|---------|-----|
| **Approval gate** | `approval_required=True` on step — blocks until `engine.approve(id)` |
| **Retry w/ backoff** | `retry_count=3, retry_delay=2.0` on Step |
| **Dead-letter queue** | Steps exhausting retries land in DLQ |
| **Conditional skip** | `skip_on_condition="state.get('skip_expensive')"` |
| **State persistence** | `persist_path="/tmp/state.json"` — checkpoint on every step |
| **Event hooks** | `on_step_start`, `on_step_success`, `on_workflow_complete`, etc. |

## DAG Execution

Uses Kahn's algorithm for topological sort. Steps at the same DAG level run in parallel. Supports `branch(condition, if_true, if_false)` for conditional paths.

## When to Use

- **tiny-workflow** → agent pipelines needing retry, approval, and crash-recovery without Temporal/Prefect overhead
- **tiny-cron** → time-based scheduling; tiny-workflow → event-driven DAG execution

## See Also

- [tiny-chain Guide](tiny-chain-guide.md) — LLM processing steps in a workflow
- [tiny-memory Guide](tiny-memory-guide.md) — agent memory across workflow runs
- [tiny-queue Guide](tiny-queue-guide.md) — persistent job queue background processing
