# tiny-cost-ledger Guide

## Repo
https://github.com/hussain-alsaibai/tiny-cost-ledger

## One-liner
Zero-dependency cost ledger with pricing tables, period rollups, and budget
alerts. Pure Python stdlib. MIT.

## Status
**Live upstream as of 2026-11-02.** The repo was created on GitHub at
17:10 UTC on 2026-11-02, *after* this guide's earlier same-day 404 re-check -
a verification is only true of the moment it was taken.

`GET /repos/hussain-alsaibai/tiny-cost-ledger` -> **HTTP 200**, MIT, default
branch `main`, `tiny_cost_ledger.py` + `tests/` + `.github/`.

```bash
pip install git+https://github.com/hussain-alsaibai/tiny-cost-ledger.git
```

## Last Verified
2026-11-02 - cloned from upstream and ran the suite: **14 passed**.
`ModelPrice(name, input_usd_per_1k, output_usd_per_1k)` verified by
`inspect.signature()` against the cloned source, not against the README.

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

Executed against upstream on 2026-11-02 (output pasted from the run).

```python
from tiny_cost_ledger import PricingTable, Ledger, Budget, CostTracker

pricing = PricingTable.defaults()
pricing.add("my-local-llm", input_usd_per_1k=0.0, output_usd_per_1k=0.0)

def alert(level, period, spent, ceiling):
    print(f"  [{level.name}] {period.value}: ${spent:.4f} / ${ceiling:.2f}")

budget = Budget(daily_usd=2.00, monthly_usd=40.00,
                threshold_alerts=(0.5, 1.0), on_alert=alert)
ledger = Ledger()                # in-memory; Ledger(path="x.jsonl") to persist
tracker = CostTracker(pricing=pricing, ledger=ledger, budget=budget, strict=True)
tracker.record("gpt-4o", tokens_in=10000, tokens_out=5000)
print(tracker.summarize())
```

**Three API corrections found by running it on 2026-11-02** (the previous
snippet in this guide used all three wrong):

1. `PricingTable(...)` takes **no positional list**. It is constructed empty
   (`PricingTable()`) or via `PricingTable.defaults()`, then `.add(name, ...)`.
2. `ModelPrice` fields are **`name`, `input_usd_per_1k`, `output_usd_per_1k`** -
   not `model`, `input_per_1k`, `output_per_1k`.
3. **`Ledger` has no `.record()` and no `.total()`**, and its constructor takes
   **no `pricing=`**. Recording is `CostTracker.record(model, tokens_in=...)`;
   aggregation is `CostTracker.summarize()` or `Ledger.query(...)`.
   `Ledger` exposes `append`, `clear`, `entries`, `path`, `query`, `reverse`.

## Key Features
- Per-model pricing tables with period-aware currency
- Period rollups (day / week / month)
- Budget objects with `AlertLevel` thresholds
- 14 tests passing (verified by run, 2026-10-23)

## Related
- `tools/tiny-cost-tracker-guide.md` — `tiny-cost-tracker` (upstream, simpler)
- `tools/tiny-llm-budget-guide.md` — runtime budget enforcement
