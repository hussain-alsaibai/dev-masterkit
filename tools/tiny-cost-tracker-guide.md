# tiny-cost-tracker — Per-Agent Token Cost Tracking & Budget Enforcement

**Repository:** https://github.com/hussain-alsaibai/tiny-cost-tracker
**Last verified:** 2026-08-28
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

Per-agent token cost tracking with built-in pricing for GPT, Claude, Gemini, Grok, and other major providers. Tracks input/output tokens, compute time, and enforces runtime USD budgets. Results persist to JSON between sessions.

## When to use

Add to any AI agent, cron job, or batch pipeline that calls LLM APIs. Prevents runaway spend by enforcing per-session or per-request USD caps with configurable warning thresholds.

## Quick start

```python
from tiny_cost_tracker import CostTracker, Model

tracker = CostTracker(budget_usd=5.0)

# Track a call
tracker.record(
    model=Model.GPT_4O_MINI,
    input_tokens=1200,
    output_tokens=340,
)

print(tracker.total_cost())      # ~$0.003
print(tracker.remaining_budget())  # ~$4.997
```

## Built-in Model Pricing

```python
from tiny_cost_tracker import Model

Model.GPT_4O_MINI      # $0.15/1M input, $0.60/1M output
Model.GPT_4O           # $2.50/1M input, $10.00/1M output
Model.CLAUDE_3_5_SONNET  # $3.00/1M input, $15.00/1M output
Model.GEMINI_1_5_FLASH  # $0.075/1M input, $0.30/1M output
Model.GROK_2           # $2.00/1M input, $10.00/1M output
```

Custom models:

```python
tracker.record(
    model="my-model",
    input_tokens=100,
    output_tokens=50,
    input_cost_per_1m=1.0,   # $1.00/1M input
    output_cost_per_1m=2.0,  # $2.00/1M output
)
```

## Budget Enforcement

```python
tracker = CostTracker(budget_usd=0.10, warn_threshold=0.8)

if tracker.exceeds_budget():
    raise RuntimeError("Budget exceeded — stopping agent")
```

## Persistence

```python
# Saves to ~/.cost_tracker.json between sessions
tracker.save()
tracker.load()
```

## Tests

Basic tests covering token counting, cost calculation, budget enforcement, and persistence.

## Last Verified: 2026-08-28

- Repo: `hussain-alsaibai/tiny-cost-tracker`
- Version: v0.1.0
- Verification: `python -m pytest` — all tests pass
