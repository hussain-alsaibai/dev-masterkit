# Cost Tracker

## What This Tool Does

Tracks all API calls and session costs across OpenClaw. Generates daily cost
reports with token usage breakdown by model.

## Installation

```bash
cd ~/.openclaw/workspace/skills/model-cost-tracker/
python cost_tracker.py
```

## Usage

### Daily Report

```bash
python -m skills.model-cost_tracker.daily_report
```

Output:
```
Daily Cost Report — 2026-06-25
- Sessions: 27
- Total tokens: ~246K
- Estimated cost: $0.00 (synthetic models)
```

### Check Specific Session

```bash
cat /tmp/session_logs/<session_id>.json | python -m skills.model-cost-tracker.ingest
```

## Key Metrics

| Metric | Description |
|--------|-------------|
| Sessions | Number of active sessions |
| Tokens | Total tokens consumed |
| Cost | Estimated USD (varies by model) |
| Records | Lifetime tracking records |

## Notes

- Synthetic models (Kimi, Qwen, Nemotron) report $0/token under subscription
- Token counts are tracked for volume analysis
- UTC/AST timezone boundary can affect daily filtering
- Fixed on 2026-06-24 to use AST timezone

## Last Verified: 2026-06-24
