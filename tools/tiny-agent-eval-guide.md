# tiny-agent-eval — Agent Evaluation Harness

**Source:** [hussain-alsaibai/tiny-agent-eval](https://github.com/hussain-alsaibai/tiny-agent-eval)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-10-23

## When to use

- Benchmarking autonomous agent behavior
- Defining pass/fail criteria for agent workflows
- Tracking regressions across agent runs
- Automated quality gates for agent-deployed PRs

## What it does

Zero-dependency agent evaluation harness for autonomous workflows. Define benchmark suites, grade agent runs, track regressions, export reports.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_eval import Benchmark,
Eval` with `Eval.grade(benchmark, agent_output)` returning `grade.score` /
`grade.passed` / `grade.criteria`. **Neither `Benchmark` nor `Eval` exists.**
Verified against upstream `tiny_eval.py`:

```
Grade, CriterionResult, EvalResult, Criterion, EvalSuite, Evaluator,
bug_fix_suite, code_quality_suite, security_suite, get_evaluator,
eval_run, eval_batch
```

The suite object is **`EvalSuite`**, criteria are **`Criterion`**, and grading
produces an **`EvalResult`** built from a **`Grade`** and per-criterion
**`CriterionResult`** values.

## Quick start

```python
from tiny_eval import EvalSuite, Criterion, eval_run

suite = EvalSuite(name="Fix bug quality", criteria=[
    Criterion("compiles without error"),
    Criterion("tests pass"),
    Criterion("no new linter warnings"),
    Criterion("PR description is present"),
])

result = eval_run(suite, agent_output)
print(result.grade.score)   # 0.75
print(result.grade.passed)  # False
```

Prebuilt suites are available for common shapes: `bug_fix_suite()`,
`code_quality_suite()`, `security_suite()`. `get_evaluator()` resolves an
evaluator, and `eval_batch()` grades multiple runs for regression tracking.

## Key features

- Named benchmark suites with pass/fail criteria
- Grade any agent context (tool calls, test results, static analysis)
- Track historical runs for regression detection
- Export reports: JSON, markdown, summary
- Zero dependencies — pure stdlib

## Ecosystem context

Part of the **tiny-*** zero-dependency ecosystem. Works with `tiny-checkpoint` (state capture), `tiny-tracer` (span recording), and `tiny-cost` (token tracking) for comprehensive agent observability.
