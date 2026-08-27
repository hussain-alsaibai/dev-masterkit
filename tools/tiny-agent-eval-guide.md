# tiny-agent-eval — Agent Evaluation Harness

**Source:** [hussain-alsaibai/tiny-agent-eval](https://github.com/hussain-alsaibai/tiny-agent-eval)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-08-27

## When to use

- Benchmarking autonomous agent behavior
- Defining pass/fail criteria for agent workflows
- Tracking regressions across agent runs
- Automated quality gates for agent-deployed PRs

## What it does

Zero-dependency agent evaluation harness for autonomous workflows. Define benchmark suites, grade agent runs, track regressions, export reports.

## Quick start

```python
from tiny_eval import Benchmark, Eval

benchmark = Benchmark("Fix bug quality", [
    "compiles without error",
    "tests pass",
    "no new linter warnings",
    "PR description is present",
])

grade = Eval.grade(benchmark, agent_output)
print(grade.score)       # 0.75
print(grade.passed)      # False
print(grade.criteria)    # breakdown per criterion
```

## Key features

- Define named benchmark suites with pass/fail criteria
- Grade any agent context (tool calls, test results, static analysis)
- Track historical runs for regression detection
- Export reports: JSON, markdown, summary
- Zero dependencies — pure stdlib

## CLI usage

```bash
python -m tiny_eval run benchmark.json --output report.md
python -m tiny_eval compare run1.json run2.json
```

## Ecosystem context

Part of the **tiny-*** zero-dependency ecosystem. Works with `tiny-checkpoint` (state capture), `tiny-tracer` (span recording), and `tiny-cost` (token tracking) for comprehensive agent observability.

## Last Verified
2026-08-27
