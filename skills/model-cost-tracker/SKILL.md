---
name: model-cost-tracker
description: Measure and report AI provider spend from the OpenClaw SQLite transcript store and the legacy usage log, merging measured token usage with estimates and pricing prompt-cache reads at their own rate. Use when asked what AI calls cost, for a daily, weekly, or monthly cost report, or to audit token usage per model.
---

# model-cost-tracker

Tracks every AI API call across all providers and generates cost reports.

## Usage

```bash
cd ~/.openclaw/workspace/skills/model-cost-tracker/
node tracker.js ingest          # legacy JSONL scan (pre-migration records only)
node tracker.js report daily    # today cost report
node tracker.js report weekly
node tracker.js report monthly

node tracker.js report daily --json
node tracker.js report weekly --model claude-sonnet-4-6
node tracker.js report monthly --task cron
node tracker.js all
```

## Data sources (read order)

1. **SQLite transcript store** - `agents/main/agent/openclaw-agent.sqlite`,
   table `transcript_events`. Authoritative since OpenClaw migrated session
   transcripts out of per-session JSONL files.
2. **Legacy `logs/usage.jsonl`** - records written before the migration.

Both are merged and de-duplicated by `(sessionId, ts, model, totalTokens)`.

> Do not reintroduce a JSONL-only scanner. `agents/main/sessions/*.jsonl` and
> `cron/runs/*.jsonl` contain **zero** `.jsonl` files now. A scanner pointed at
> them reports "0 new records from 0 updated files" forever while real spend
> continues. That failure mode cost us ~5 days of blind cost reporting.

## Measured vs estimated

Providers that honor `stream_options.include_usage` return real token counts.
Providers that do not (MiniMax currently) return an all-zero usage block, so
token counts are unrecoverable from the provider. In that case the tracker
falls back to estimating from transcript text volume (chars / 3.6) and prices it
with published per-model rates. Estimates are flagged and printed as
`~ ESTIMATED: n/m calls` so they are never mistaken for measured values.

To get true measured numbers, enable usage in streaming for the provider:

```json
"models": { "providers": { "minimax": { "models": [
  { "id": "MiniMax-M3", "compat": { "supportsUsageInStreaming": true } }
] } } }
```

### Estimated usage is merged with measured, never instead of it

Two bugs shipped here on the same day (2026-10-24), both of the same shape:
**a number that looked like data and was not**.

1. **Estimated usage replaced measured usage** (fixed 2026-10-24). The
   tracker wrote the estimate over the real provider figure, so every report
   was an upper bound that also discarded the one number we actually had.
   The fix merges the two instead of substituting one for the other. Effect:
   the daily report went from `$0.00 / 0 calls` to **$78.10 across 1,574
   calls and 132.3M tokens**.
2. **The prompt cache was priced as fresh input** (fixed 2026-10-24). See
   below — this one was a **4x** overstatement.

### Pricing the cache (do not skip this)

MiniMax **does** cache prompts, and the cache is not optional detail — it is
97% of the prompt. A usage block looks like:

```json
{ "input": 716, "output": 497, "cacheRead": 397211, "cacheWrite": 0 }
```

The fresh input is tiny; the context is served from cache at $0.12/1M instead
of $0.60/1M. Pricing a whole prompt at the fresh-input rate overstates cost
**~4x**.

The estimator therefore splits the prompt:
- `PROMPT_SCALE = 1.36` — the estimator only counts `msg.content` length and
  misses tool-call payloads and system framing, so it must scale up. Measured
  as `sum(truePrompt) / sum(estimatedPrompt)` over measured calls.
- `CACHE_SHARE` (0.97 for MiniMax) — the share of the prompt served from cache,
  priced at `price.cacheRead`; the remainder at `price.input`.

Both constants are measured, not guessed. Re-derive them whenever the pricing
or provider changes:

```bash
node -e "
const {collectRecords}=require('./sqlite-source.js');
// A = sum(input+cacheRead) / sum(estimatedPrompt) over measured calls
// C = sum(cacheRead) / sum(input+cacheRead)
"
```

**Validated 2026-10-24** against 440 measured calls: old estimator was 3.99x
overstated, new estimator is 0.92x of truth. If a report looks 3-4x higher than
a hand-computed number, the cache pricing is the first thing to check.

> Do not price a cached prompt as fresh input. The provider's own `cacheRead`
> counter is the ground truth for what was billed.

## Storage
- `logs/usage.jsonl` - legacy append-only log (pre-migration records only)
- `logs/ingest-state.json` - tracks which legacy session files were processed

## Fields per record
- `ts` - ISO timestamp
- `sessionId` - source session
- `taskType` - cron | main-session | subagent | other
- `provider` / `model`
- `inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens`
- `costInput`, `costOutput`, `costCacheRead`, `costCacheWrite`, `costTotal`
- `estimated` - true when derived from transcript volume rather than the provider

## Notes
- OpenClaw 2026.10.4 / Node 24.21.0. `node:sqlite` requires Node >= 22.5.
- Transcript rows are zstd-compressed (`event_zstd`) or plain JSON (`event_json`);
  both are decoded.
- MiniMax API rates (USD per 1M tokens): M3 input 0.6 / output 2.4 / cacheRead 0.12.

## Scheduled Reports
- Cron: daily at 9 PM AST → posts to Telegram group

## Last Verified: 2026-10-24
