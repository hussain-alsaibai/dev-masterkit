# tiny-cost-ledger Guide

## Repo
https://github.com/hussain-alsaibai/tiny-cost-ledger

## One-liner
Zero-dependency cost ledger with pricing tables, period rollups, and budget
alerts. Pure Python stdlib. MIT.

## Status
**Repo does not exist upstream yet** (`https://github.com/hussain-alsaibai/tiny-cost-ledger`
-> HTTP 404, checked 2026-10-23). Local clone only.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_cost_ledger import
CostLedger, Model, Period`. **Neither `CostLedger` nor `Model` exists.**
Verified against the local clone:

```
AlertLevel, Period, CostEntry, ModelPrice, PricingTable, Ledger,
Budget, CostTracker
```

The ledger is **`Ledger`**, the pricing table is **`PricingTable`** (with
`ModelPrice` records), the period enum is **`Period`**, alerts use
**`AlertLevel`**, and there is a **`Budget`** type plus a **`CostTracker`**.

## Quick Example
```python
from tiny_cost_ledger import Ledger, ModelPrice, PricingTable, Period

pricing = PricingTable([ModelPrice(model="gpt-5", input_per_1k=0.01, output_per_1k=0.03)])
ledger = Ledger(pricing=pricing)
ledger.record(model="gpt-5", input_tokens=1200, output_tokens=400)
print(ledger.total(Period.MONTH))
```

## Key Features
- Per-model pricing tables with period-aware currency
- Period rollups (day / week / month)
- Budget objects with `AlertLevel` thresholds
- 14 tests passing (verified by run, 2026-10-23)

## Related
- `tools/tiny-cost-tracker-guide.md` — `tiny-cost-tracker` (upstream, simpler)
- `tools/tiny-llm-budget-guide.md` — runtime budget enforcement
