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

## W3C Trace Context (v0.6.0, 2026-11-02)

`tiny-log` v0.6.0 ships **W3C trace context**. `TraceContext` binds
`trace_id`, `span_id`, `parent_span_id`, `flags` and `tracestate` to the
current log scope, so every record emitted inside the context carries them.

```python
from tiny_log import TraceContext

# start a new trace
with TraceContext() as tc:
    log.info("working", repo="fast-cache")
    headers = tc.as_headers()        # -> {'traceparent': '00-<32hex>-<16hex>-01'}

# continue an incoming trace
with TraceContext.from_headers(incoming) as tc:
    log.info("continuing")
```

Standalone helpers: `parse_traceparent(value)`,
`inject_traceparent(...)`, `new_span_id()` (16 hex),
`new_w3c_trace_id()` (32 hex). The existing `new_trace_id()` keeps its
24-hex OpenTelemetry display form.

### The bug that shipped with the feature

The first implementation minted a **new** trace id inside `as_headers()`,
so the traceparent it emitted pointed at a different trace than the log
records emitted alongside it. **Downstream requests landed in a different
trace than the logs describing them.** Ported from a stale clone, where the
guard did not exist.

Fixed, and pinned by **20 tests** in
`tests/test_tiny_log_v060_trace.py`. **3 of them fail if the trace-continuity
guard is removed** - the regression is proven, not asserted.

### Why this matters for an evidence log

An evidence bundle whose records and outbound requests carry **different
trace ids** is not a traceable bundle. The trace id is the join key between
"what the agent did" and "what it called". A mismatch makes the two halves
unjoinable, and there is no error - it just looks like two unrelated
histories.

## Last verified: 2026-11-02

- Repo: `hussain-alsaibai/tiny-log` - v0.6.0, **98 tests passing** (measured
  by run)
- The v0.6.0 trace-context API above was verified by import and by running
  the suite, not by reading the changelog.
- Earlier verification: local field note
  `reports/2026-07-15-agent-audit-bundles.md`, reviewed during the July 15
  developer-tools report run.
