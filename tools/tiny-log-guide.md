# tiny-log - Structured Evidence Logs

## Repo

https://github.com/hussain-alsaibai/tiny-log

## One-liner

Zero-dependency structured logging for agent workflows: JSONL evidence, bound
context, timing helpers, and readable terminal output.

## When to Use

- A cron job, webhook receiver, or agent run needs a reviewable trail.
- You need to explain skipped work as clearly as completed work.
- You want machine-readable JSONL without adding an observability service.
- A final report should link back to the events that produced it.

## Agent Audit Bundle Pattern

Pair a JSONL evidence stream with a short Markdown summary. The JSONL file is
for machines and later dashboards; the Markdown is for the operator reviewing
the run.

Recommended event vocabulary:

- `started`
- `claimed`
- `skipped`
- `validated`
- `executed`
- `retried`
- `reported`
- `failed`

Recommended bound fields:

- `goal_id`
- `cron_id`
- `repo`
- `issue`
- `tool`
- `attempt`
- `decision`

## Example Events

```json
{"event":"started","cron_id":"daily-dev-masterkit-update","repo":"dev-masterkit"}
{"event":"claimed","repo":"fast-cache","lease_ttl":900,"decision":"run"}
{"event":"skipped","repo":"tiny-router","reason":"no verified change today"}
{"event":"reported","artifact":"daily-updates/2026-07-15.md"}
```

## Operational Checklist

- Log skipped actions deliberately; a safe no-op is still a decision.
- Redact common secret-bearing fields such as `token`, `password`, `secret`,
  `authorization`, and `api_key`.
- Include correlation fields that survive across retries and summaries.
- Keep live terminal output readable, but write audit artifacts as JSONL.
- Pair audit events with validation errors from `tiny-validator` and lease
  decisions from `fast-cache`.

## Last verified: 2026-07-15

- Repo: `hussain-alsaibai/tiny-log`
- Verification: local field note
  `reports/2026-07-15-agent-audit-bundles.md` was reviewed during the July 15
  developer-tools report run. The reusable pattern is documentation/procedure
  only; no new `tiny-log` code was required for this guide.
