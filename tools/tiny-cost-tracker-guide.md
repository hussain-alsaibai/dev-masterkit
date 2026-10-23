# tiny-cost-tracker Guide

## Repo
https://github.com/hussain-alsaibai/tiny-cost-tracker

## What It Does

Zero-dependency token cost tracking for AI agents. One file, no setup. Built-in
model pricing, per-run totals, and budget circuit breaking.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_cost_tracker import
CostTracker, Model`. **There is no `Model` class.** Verified against upstream
`tiny_cost_tracker.py`:

```
ModelPricing, CostEntry, CostTracker
```

The pricing record is **`ModelPricing`** (a dataclass describing a model's
per-token rates), the individual charge is **`CostEntry`**, and the tracker is
**`CostTracker`**.

## Quick Start

```python
from tiny_cost_tracker import CostTracker, ModelPricing

tracker = CostTracker(pricing={"gpt-5": ModelPricing(input_per_1k=..., output_per_1k=...)})
tracker.record(model="gpt-5", input_tokens=1200, output_tokens=400)
print(tracker.total_usd)
```

## When to Use

- Charging agent runs against a budget
- Reporting what a cron job or tool call actually cost
- Blocking a run that has exceeded its budget

## Related

- `tools/tiny-budget-ledger-guide.md` — `tiny-cost-ledger`, a different repo (local only)
- `tools/tiny-llm-budget-guide.md` — runtime token/USD budget enforcement
