# tiny-eval — Zero-Dependency Agent Evaluation Framework

**Repo:** `hussain-alsaibai/tiny-eval`
**Version:** 0.1.0 | **Dep:** Zero (stdlib only) | **License:** MIT
**Last verified:** 2026-10-28 — **63 tests passing** (measured by run against the
upstream clone; was 0 CI). The package had **no CI** until 2026-10-28.

Define benchmark suites, grade agent runs, and track score regressions over
time — pure stdlib, no model dependency.

## API Correction (2026-10-28) — the previous guide documented a different package

The previous version of this guide described a **sandboxed expression
evaluator** and told readers to run:

```python
from tiny_eval import eval_expr, Sandbox, interpolate
```

**None of `eval_expr`, `Sandbox` or `interpolate` exists.** They are zero
matches against the real source. The actual public surface is:

```
__all__ = [
    "Score", "Criterion", "Rubric",
    "BenchmarkCase", "BenchmarkSuite",
    "EvalResult", "SuiteResult",
    "RegressionReport", "RegressionTracker",
    "AgentRunner", "TinyEvalCLI",
    "bug_fix_suite", "code_quality_suite", "security_suite", "context_efficiency_suite",
]
```

The package is an **agent evaluation framework**, not a sandbox. A reader who
copied the old snippet got an `ImportError` on the first line.

**Why this happened:** `tiny-eval` on PyPI belongs to a **different** TinyEval
("A tiny evaluation framework for language models", v0.5.0). Our README's
PyPI version badge pointed at it, so the rendered version number was never
this project's version. The badge now points at the GitHub install instead.

**Name collision (verified 2026-10-28):** `pip install tiny-eval` installs
**someone else's** package. Install from the repository URL:

```bash
pip install "git+https://github.com/hussain-alsaibai/tiny-eval.git"
```

## Quick Start

```python
from tiny_eval import BenchmarkCase, BenchmarkSuite, Criterion, Rubric, Score

rubric = Rubric([
    Criterion(
        name="tests_pass",
        description="the agent's patch makes the suite green",
        weight=1.0,
        evaluate_fn=lambda task, response: Score(
            value=1.0 if response.get("tests_pass") else 0.0,
            reason="tests_pass",
        ),
    ),
])

case = BenchmarkCase(
    task_id="off-by-one",
    description="Fix the off-by-one in the loop bound",
    task_fn=lambda: {"file": "loop.py", "bug": "off-by-one"},
    expected_fn=lambda: {"file": "loop.py", "bug": "fixed"},
    rubric=rubric,
    pass_threshold=0.7,
)

suite = BenchmarkSuite(name="bug-fix", cases=[case])
result = suite.run(agent_fn)
print(result.pass_rate)   # fraction of cases above their threshold
print(result.avg_score)   # mean weighted score, 0.0 - 1.0
```

`BenchmarkSuite.run(agent_fn)` calls `agent_fn` for each case, evaluates the
response with the case's `Rubric`, and returns a `SuiteResult` carrying
`pass_rate`, `avg_score`, `total_cost`, `total_duration_ms` and the
per-case `EvalResult` list.

## Key Features

| Feature | Description |
|---|---|
| **Benchmark suites** | cases with prompts, scoring functions, thresholds |
| **Agent grading** | run any agent function against a suite, get per-case scores |
| **Regression tracking** | compare each run against history, detect score drops |
| **CI integration** | block merges on an eval regression, like a test suite |
| **Zero dependencies** | pure stdlib, auditable in an afternoon |

## Built-in suites

`bug_fix_suite`, `code_quality_suite`, `security_suite` and
`context_efficiency_suite` ship in the package as ready-made suites.

## When to Use

- "Does the agent actually work?" as a CI gate rather than a vibe check
- Catching a refactor that silently degrades agent behaviour
- Comparing two prompts, two models, or two agent designs on the same cases

## Related

- `tools/tiny-evaluator-guide.md` — `tiny-evaluator`, a **different** package
  with streaming-aware test runners, LLM-as-judge and HTML reports
- `tools/tiny-agent-eval-guide.md` — `tiny-agent-eval`, the third member of
  this family. Three different packages, three different names, three
  different APIs — check which one you actually want before copying a snippet.
- `prompts/pypi-name-collision-is-a-silent-success.md` — why the collision
  mattered and how it was fixed
