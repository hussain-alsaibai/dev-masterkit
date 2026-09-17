# tiny-budget-ledger — File-Backed Per-Task Spend Ledger

> File-backed per-task spend ledger for autonomous AI agents. Stdlib only.
> Last verified: 2026-09-17 | Version 0.1.0 | hussain-alsaibai/tiny-budget-ledger

## What It Is

A crash-safe append-only JSONL ledger that tracks USD and token spend against per-task and monthly caps, and refuses new spends that would push a budget over its limit. Thread-safe and asyncio-friendly.

- Per-task USD cap (`per_task_usd`)
- Monthly USD cap (`monthly_usd`)
- Monthly token cap (`monthly_tokens`)
- Sync `BudgetLedger` + async `BudgetLedgerAsync` wrapper
- Warn / block / monthly rollover callbacks
- Hooks for `tiny-cost-tracker` and `tiny-llm-router`
- 16/16 tests passing, MIT, ~7 KB single file

## Why It Exists

OpenClaw's core operating principle (SOUL.md) is **every session must produce more value than it consumes**. To enforce that we need:

1. A ledger that survives crashes (append-only JSONL, `fsync` per write)
2. Per-task and global budgets in USD and tokens
3. A small sync `BudgetLedger` and an async `BudgetLedgerAsync` wrapper
4. Callbacks for warn / block / monthly rollover
5. Hooks for `tiny-cost-tracker` and `tiny-llm-router`

Cron jobs, multi-tenant agents, per-model-per-task budget gates — every autonomous setup needs this layer.

## Repo

https://github.com/hussain-alsaibai/tiny-budget-ledger

## When to Use

- You run cron jobs that spend API tokens and need hard caps
- You want a "refuse to spend if it would exceed budget" guard before each LLM call
- You need a per-task ledger to attribute spend back to originating work (bounty scan, daily report, repo update)
- You're wiring `tiny-cost-tracker` ingest and need the upstream source-of-truth

## Minimal Example

```python
from tiny_budget_ledger import BudgetLedger

led = BudgetLedger(
    path="/var/lib/openclaw/budget.jsonl",
    monthly_usd=50.0,
    monthly_tokens=20_000_000,
    per_task_usd=5.0,
)

led.record_spend(task_id="bounty-hunt", usd=0.05, tokens=4200,
                 model="kimi-k2.6", note="scanned 22 issues")

if not led.can_spend(usd=2.0, tokens=200_000):
    raise SystemExit("Aborted: budget cap would be exceeded")

print(led.summary())
# {'month': '2026-09', 'month_usd_spent': 0.05, ...
```

## Tested Patterns

- Crash recovery from partial JSONL tail (re-reads last valid line)
- Concurrent writers via `fcntl.flock`
- Async wrapper with `asyncio.Lock`
- Monthly rollover callback fires once per UTC month
- Hook into `tiny-llm-router.record()` after each call

## See Also

- `tools/cost-tracker.md` — downstream aggregator
- `tools/tiny-llm-router-guide.md` — pair the two for per-call gating
- `prompts/cost-tracker-session-ingest.md` — session ingest path
