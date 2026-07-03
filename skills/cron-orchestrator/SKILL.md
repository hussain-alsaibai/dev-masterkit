# cron-orchestrator — Skill for Setting Up Automated Monitoring Jobs

## Trigger

Use when the user asks to:
- "Set up a cron job for..."
- "Automate [task] to run daily/weekly"
- "Monitor [service] on a schedule"
- "Create a recurring check"
- "Add automated reporting"

## Description

Creates and manages cron jobs for automated monitoring, reporting, and
maintenance tasks using the OpenClaw cron system.

## Procedure

### 1. Define the Job

Determine:
- **Task:** What to do (bounty scan, health check, repo monitor)
- **Frequency:** How often (daily, weekly, every N hours)
- **Schedule:** Exact time in user's timezone (AST for The Architect)
- **Output:** Where results go (Telegram thread, log file, webhook)
- **Failure action:** Alert channel if job fails

### 2. Choose Schedule Type

| Frequency | Schedule Kind | Example |
|-----------|--------------|---------|
| Once at specific time | `at` | `"2026-06-26T09:00:00Z"` |
| Every N minutes/hours | `every` | `"everyMs": 3600000` (1 hour) |
| Daily at specific time | `cron` | `"expr": "0 9 * * *", "tz": "Asia/Bahrain"` |
| Weekly on specific day | `cron` | `"expr": "0 9 * * 0", "tz": "Asia/Bahrain"` |

### 3. Build the Cron Job

```json
{
  "name": "daily-bounty-scan",
  "description": "Scan Algora and Opire for coding bounties",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "Asia/Bahrain"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the bounty scanner...",
    "model": "synthetic/hf:moonshotai/Kimi-K2.6"
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "-1003802123109"
  }
}
```

### 4. Set Delivery Target

| Target Type | Use When |
|-------------|----------|
| `main` | System events, heartbeat checks |
| `isolated` | Independent tasks that don't need session context |
| `current` | Tasks that need current session context |
| `session:<id>` | Specific persistent session |

### 5. Add Failure Alerts (Optional)

```json
"failureAlert": {
  "mode": "announce",
  "channel": "telegram",
  "to": "-1003802123109",
  "after": 2,
  "cooldownMs": 3600000
}
```

### 6. Verify and Monitor

After creating:
1. Check job status: `cron action=list`
2. Force run once: `cron action=run jobId=<id> runMode=force`
3. Monitor runs: `cron action=runs jobId=<id>`
4. Check logs for errors

## Example Jobs

### Daily Bounty Scanner

```json
{
  "name": "daily-bounty-work",
  "schedule": { "kind": "cron", "expr": "0 10 * * *", "tz": "Asia/Bahrain" },
  "payload": {
    "kind": "agentTurn",
    "message": "Scan Algora and Opire for bounty issues. Filter scams. Start top issue."
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce", "to": "-1003802123109" }
}
```

### Weekly Multi-Platform Status

```json
{
  "name": "weekly-platform-status",
  "schedule": { "kind": "cron", "expr": "0 9 * * 0", "tz": "Asia/Bahrain" },
  "payload": {
    "kind": "agentTurn",
    "message": "Check all platform statuses..."
  },
  "sessionTarget": "isolated"
}
```

## Validation Checklist

- [ ] Job has descriptive name (kebab-case)
- [ ] Schedule uses user's timezone (Asia/Bahrain for AST)
- [ ] Payload message is specific and actionable
- [ ] Delivery target matches output destination
- [ ] Failure alerts configured for critical jobs
- [ ] Job tested with force run before leaving
- [ ] Job appears in `cron list` output

## Notes

- Use `isolated` sessions for independent tasks to avoid polluting main session
- Batch similar checks into heartbeats rather than creating many cron jobs
- Use `cron` not exec sleep/polling for scheduled tasks
- Include `lightContext: true` for long-running jobs to reduce token usage
- Keep payload messages under 200 tokens for faster processing

## Stagger Policy (added 2026-06-30)

When multiple agentTurn jobs share the same `cron` minute field, add `staggerMs`
to the schedule to prevent RPM (requests per minute) bursts against the model
provider:

```json
"schedule": {
  "kind": "cron",
  "expr": "0 21 * * *",
  "tz": "Asia/Bahrain",
  "staggerMs": 45000
}
```

- **Pick a unique stagger per job** — using the same value just shifts the burst.
- **Range:** 30–90s typical; up to 60s×N if you have N jobs sharing the minute.
- **Symptom of a missing stagger:** recurring `429 rate limit exceeded (RPM)`
  errors in cron runs (e.g. `self-evolution-4h-report` failures).
- See `prompts/cron-stagger-rpm.md` for the full diagnostic prompt.

## Webhook Server Checklist (added 2026-07-02)

When a cron announcement targets a webhook (FalconEye, Slack, etc.), the receiving
endpoint should:

- **Short-circuit `HEAD` and empty-body `POST` to `204 No Content`** before any
  JSON parse runs. Health probes and keepalive pings will otherwise fill the log
  with `Unexpected end of JSON input` errors that distract from real failures.
- **Limit body size** with `Content-Length` reading + `request.body.read(max_bytes)`.
- **Return within 10 seconds** — long-running handlers belong in a worker, not the
  webhook thread.

## Last Verified: 2026-07-03

## Last Verified: 2026-06-30
