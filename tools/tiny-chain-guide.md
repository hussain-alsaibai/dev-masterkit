# tiny-chain Guide

> Structured chain-of-thought tracing for AI agents. Records, structures, and exports reasoning steps as machine-readable JSON traces with timing, metadata, and evaluation hooks. ~600 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-chain
**Last Verified:** 2026-09-04

## Quick Start

```python
from tiny_chain import TinyChain

chain = TinyChain("issue-fix", tags=["bounty-hunter"])

@chain.step("Triage", "Identifying affected files")
def triage(issue):
    return {"affected": ["src/main.py"]}

@chain.step("Fix", "Applying the fix")
def apply_fix(affected):
    return "patched"

chain.run({"issue": "NPE on startup"})
print(chain.summary())
```

## Key Patterns

| Pattern | API |
|---------|-----|
| **Streaming** | `for chunk in chain.stream(prompt): print(chunk.content, end="")` |
| **Model fallbacks** | `chain.complete_with_fallback("gpt-4o", ["gpt-4o-mini"], prompt)` |
| **Function calling** | `chain.complete(prompt, functions=[weather_func])` |
| **JSON extraction** | `json_extractor.extract_json(text)` |
| **Structured output** | `structured_output(prompt, schema)` |
| **Multi-step span** | `@chain.span("Analyze", "Reviewing code"):` |
| **Scoring** | `chain.score("clarity", 0.9); chain.score("correctness", 1.0)` |
| **Grading** | `passed, avg = chain.grade({"clarity": 0.7, "correctness": 0.8}, 0.75)` |
| **Snapshot** | `snap = chain.snapshot()` — point-in-time for async/parallel workflows |
| **Export** | `chain.export("run.json")`; `TinyChain.from_dict(data)` to reload |

## v0.2.0 Key Additions

- **`span()` context manager** — for reasoning steps spanning multiple function calls
- **`score()` / `grade()`** — first-class evaluation hooks; score chains against named criteria, pass/fail against rubric threshold
- **`snapshot()`** — point-in-time capture for async and multi-agent workflows
- **`export()` / `from_dict()`** — full round-trip JSON serialization
- **`to_compact_dict()`** — minimal format for logging (chain ID, step names, durations only)
- **Error propagation** — exceptions in decorated functions are recorded as failed steps and re-raised
- **Tags & metadata** — per-step and per-chain classification for filtering

## Integration: tiny-chain + tiny-eval

Chain traces feed directly into eval pipelines:

```python
from tiny_eval import EvalSuite, RegressionTracker

suite = EvalSuite("bug-fix-benchmark", cases=[...])
run = suite.run(lambda p: agent.run(p))
tracker = RegressionTracker("eval_runs.json")
result = tracker.record(run)
```

## When to Use

- **tiny-chain** → structured CoT tracing + scoring for agent workflows
- **tiny-mcp** → exposing tools via MCP protocol instead of direct function calls
- **tiny-eval** → automated grading of agent outputs against rubrics

## See Also

- [tiny-eval Guide](tiny-eval-guide.md) — zero-dep agent evaluation framework
- [tiny-workflow Guide](tiny-workflow-engine-guide.md) — DAG orchestration for multi-step chains
