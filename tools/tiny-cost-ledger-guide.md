# tiny-cost-ledger Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-cost-ledger
**Last verified:** 2026-09-22
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

Itemized LLM cost ledger with multi-period budgets and alert hooks. Tracks per-call LLM spend (input/output tokens, model, time), enforces per-period budgets (daily/weekly/monthly), and emits structured alerts when thresholds are crossed.

## When to use

Drop into any autonomous agent, cron, or batch pipeline that calls closed-source LLM APIs. Distinct from `tiny-cost-tracker` (which is in-memory, per-session); this is a persistent, multi-period ledger with alerting.

## Quick start

```python
from tiny_cost_ledger import CostLedger, Model, Period

ledger = CostLedger(periods=[Period.DAILY, Period.WEEKLY, Period.MONTHLY])

@ledger.record(model=Model.GPT_4O_MINI)
def call_llm(prompt):
    ...

# Thresholds + alert hooks
ledger.on_threshold(usd=5.0, period=Period.DAILY, callback=alert_team)
```

## Key features

- **Multi-period budgets** — daily, weekly, monthly envelopes
- **Default pricing 2026 Q3** — GPT, Claude, Gemini, Grok
- **Strict mode** — refuse uncategorized models
- **Alert hooks** — callback on threshold breach
- **Persistent JSON** — survives across sessions
- **Single file** — auditable in one sitting

## Integration pattern

Stack on top of `tiny-cost-tracker` (per-session, in-memory) for a full spend picture: tracker handles a single agent's runtime budget; ledger handles org/team-level multi-period caps.

## Notes

- Created 2026-09-22 as part of the tiny-* ecosystem
- MIT licensed, zero dependencies
- Tests in `tests/`
