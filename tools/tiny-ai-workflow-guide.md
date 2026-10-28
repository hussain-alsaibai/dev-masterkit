# tiny-ai-workflow Guide

## Repo
https://github.com/hussain-alsaibai/tiny-ai-workflow

## What It Does

Step-function style AI pipeline for Python. One file, no setup. Sequence,
parallel, conditional, and loop steps with per-step error handling.

## Last Verified
2026-10-28 - **12 tests passing** (measured by run against the upstream clone;
was 3 passed / 9 failed). The package had **no CI** until 2026-10-28, and
adding it found a defect that made the library unusable.

## The `WorkflowStep` Defect (fixed 2026-10-28)

`@wf.step()` could **never** work:

```python
# BROKEN - `default_factory` is a CALLABLE that dataclasses invokes
result: Any = field(default_factory=None, init=False)

# CORRECT
result: Any = field(default=None, init=False)
```

Passing `None` as the factory means dataclasses calls `None()`, which raises
`TypeError: 'NoneType' object is not callable` on **every single step
registration**. 9 of the 12 tests failed for this reason.

One test was also asserting the opposite of the documented behaviour: it
checked that a step which *succeeded* appears in `failed_steps()`. The library
is right - `failed_steps()` returns only steps whose state is `failed` - so the
test was inverted.

Packaging was fixed in the same pass: the wheel shipped no importable module,
because `[tool.setuptools.packages.find]` with `include = ["tiny_ai_workflow*"]`
finds nothing (a single module is not a package). It now uses
`[tool.setuptools] py-modules = ["tiny_ai_workflow"]`.

The PyPI name `tiny-ai-workflow` is **free** (verified 2026-10-28); the
package is not published there yet.

## Previous verification
2026-10-23
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
