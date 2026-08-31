# tiny-ai-workflow Guide

> Step-function workflow engine for AI pipelines. Supports sequence, parallel, conditional, loop, and error-handling steps. ~577 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-ai-workflow
**Last Verified:** 2026-08-31

## Quick Start

```python
from tiny_ai_workflow import Workflow, Sequence, Parallel, Conditional, Loop

wf = Workflow()
wf.add_step("fetch", fetch_data)
wf.add_step("transform", transform_data)
wf.add_step("validate", validate_data)
result = wf.run(initial_input)
```

## Step Types

- **Sequence** — Run steps in order
- **Parallel** — Run steps concurrently
- **Conditional** — Branch based on step output
- **Loop** — Repeat until condition or max iterations

## When to Use

- Multi-step AI pipelines (fetch → enrich → validate → respond)
- Agentic workflows with branching logic
- Batch processing with error recovery

## Key Features

- Async-first design
- Error-handling with retry / fallback
- State passed between steps via context dict
- Zero dependencies
