# model-cost-tracker

Tracks every AI API call across all providers and generates cost reports.

## Usage

```bash
# Scan all sessions and ingest new records
node tracker.js ingest

# Reports (auto-ingests first)
node tracker.js report daily
node tracker.js report weekly
node tracker.js report monthly

# Filter by model
node tracker.js report weekly --model claude-sonnet-4-6
node tracker.js report monthly --model claude-opus

# Filter by task type (cron | main-session | other)
node tracker.js report weekly --task cron

# JSON output (for scripting)
node tracker.js report daily --json

# All three periods at once
node tracker.js all
```

## Storage
- `logs/usage.jsonl` — append-only log of every API call with cost
- `logs/ingest-state.json` — tracks which session files have been processed

## Fields logged per call
- `ts` — ISO timestamp
- `sessionId` — source session
- `taskType` — cron | main-session | other
- `provider` — anthropic | google | openai | xai
- `model` — full model ID
- `inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens`
- `costInput`, `costOutput`, `costCacheRead`, `costCacheWrite`, `costTotal`

## Scheduled Reports
- Cron: daily at 9 PM AST → posts to Telegram group
