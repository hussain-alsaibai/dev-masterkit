# tiny-budget — Runtime Budget Enforcement for AI Agents

## Repo
https://github.com/hussain-alsaibai/tiny-budget

## One-liner
Zero-dependency USD and token budget guard for AI agent calls, with atomic JSON persistence so a crashed process does not double-spend after restart.

## Install
```bash
npm install tiny-budget
```

## Quick Example

```js
import { Budget, BudgetExceeded } from "tiny-budget";

const budget = new Budget({
  taskId: "daily-cron-2026-07-06",
  limitUsd: 1.0,
  limitTokens: 100_000,
  path: "./budget-state.json"
});

try {
  budget.chargeUsage({
    model: "gpt-4.1-mini",
    usage: {
      prompt_tokens: 1200,
      completion_tokens: 300
    }
  });
} catch (error) {
  if (error instanceof BudgetExceeded) {
    // Stop the agent loop before the bill runs away.
  }
}
```

## Properties

| Property | How |
|----------|-----|
| USD limits | Per-model input/output token pricing |
| Token limits | Prompt + completion token accounting |
| Crash safety | Write-temp + rename JSON persistence |
| Task isolation | `taskId` scopes spend to one unit of work |
| Provider support | OpenAI and Anthropic usage shapes out of the box |
| Opaque APIs | `chargeFlat()` for one-off fixed-cost calls |
| Extensibility | `setPricing()` for custom model tables |
| Warnings | Threshold callback fires once per crossing |

## CLI

```bash
tiny-budget price gpt-4.1-mini
tiny-budget simulate --limit-usd=1.00 ./charges.jsonl
```

## Testing

- **16/16 tests passing**
- Verified with Node's built-in test runner
- 0 runtime dependencies

## Agent workflow fit

Use `tiny-budget` at the boundary around any call that can spend money:

1. Validate inbound work with `tiny-validator`.
2. Load per-task caps from `tiny-config`.
3. Check and charge with `tiny-budget`.
4. Execute the model/tool call.
5. Emit the result or rejection via `tiny-eventbus`.

This pattern keeps cron jobs and autonomous loops from silently exceeding a daily or per-task cap.

Last verified: 2026-07-06
