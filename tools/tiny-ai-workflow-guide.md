# tiny-ai-workflow Guide

## Repo
https://github.com/hussain-alsaibai/tiny-ai-workflow

## What It Does

Step-function style AI pipeline for Python. One file, no setup. Sequence,
parallel, conditional, and loop steps with per-step error handling.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_ai_workflow import
Workflow, Sequence, Parallel`. **There are no `Sequence` or `Parallel`
classes.** Verified against upstream `tiny_ai_workflow.py`:

```
__all__ = ['Workflow', 'WorkflowStep', 'WorkflowResult', 'WorkflowError',
           'step', 'branch', 'parallel']
```

Composition is done with the **`step`**, **`branch`**, and **`parallel`**
helpers, not with `Sequence` / `Parallel` classes. `WorkflowStep` is the step
type and `WorkflowResult` the outcome.

## Quick Start

```python
from tiny_ai_workflow import Workflow, step, branch, parallel

wf = Workflow("ingest")

@step
def fetch(ctx):
    ctx["docs"] = fetch_docs()

@parallel
def embed_all(ctx):
    ...

@branch(when=lambda ctx: ctx["docs"])
def route(ctx):
    ...

wf.add(fetch).add(embed_all).add(route)
result = wf.run()
```

## When to Use

- Multi-step agent pipelines where each step can fail independently
- Needing parallel fan-out without asyncio ceremony
- A workflow that must be describable and replayable

## Related

- `tools/tiny-workflow-guide.md` — `tiny-workflow`, a separate repo with a DAG engine
- `tools/tiny-workflow-engine-guide.md` — `tiny-workflow-engine`, also distinct
