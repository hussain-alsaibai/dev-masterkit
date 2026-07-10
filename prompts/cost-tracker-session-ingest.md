# Cost tracker silent because nothing calls start/end on new sessions

## What this solves

When you build a "cost tracker" that aggregates per-session spend into a
JSON file (`memory/cost-tracker/data.json` or similar) by hooking into the
agent harness's session-start / session-end events, **the tracker can go
silent forever** if the wiring is incomplete — and the silent failure
mimics "free sessions" (cost shows `$0`) without any error.

## Symptoms

- `cost-tracker/data.json` `last_updated` date stops advancing, even though
  sessions are clearly running.
- Dashboard / cron reports show `$0.00 today` for days or weeks.
- No error in logs — the tracker process is healthy, just receiving zero
  events.
- Daily / weekly summaries drift further and further behind reality, but
  the UI never flags the staleness.

## Why it happens

Most agent harnesses expose a *per-session* lifecycle hook, but if your
tracker only registers once at startup and expects the harness to push
events to it, the moment a new session is spawned (cron, sub-agent,
isolated run, fresh main session after a restart) it bypasses the
registration entirely. The tracker happily reports its old state.

Common shapes that produce this:

- Tracker registered in `main` session bootstrap only.
- Tracker expects a single long-lived parent; sub-agents / crons never
  inherit the hook.
- `pidfile`-based singleton: stale PID blocks re-registration after a
  crash, but old PID's events were never flushed.
- Tracker uses an in-process event bus instead of a durable queue — once
  the parent dies, queued events vanish.

## Fix pattern

1. **Make registration idempotent and self-healing.** On every cron /
   heartbeat / agent turn, *re-check* that the tracker is reachable and
   re-register if not. Treat silence longer than N hours as a hard alarm,
   not just "no spend today".
2. **Use a durable sink.** Append-only JSONL (`<ts> <session_id> <cost>
   <model>`) is enough. Roll up to `data.json` lazily. Lose nothing on
   crash.
3. **Instrument the missing events at the source.** If your harness
   exposes a `onSessionStart` / `onSessionEnd` hook, call the tracker from
   *every* entry point: main, cron, sub-agent spawn, fallback model.
4. **Add a staleness check to your daily-evolution cron.** If
   `data.json.last_updated` is older than 24h and you ran sessions today,
   flag it as yellow/red, not as "free day".

## Last verified

- 2026-07-10 — `daily-evolution-report` cron at 14:00 ET reported `$0 today`
  because `cost-tracker/data.json` `last_updated` was 2026-06-30 despite
  ~90 sessions/week (gemini-2.5-flash + gpt-5.5). Root cause: tracker only
  registered on the original main-session bootstrap; subsequent cron /
  sub-agent sessions never call start/end. Synthetic subscription
  (`$0/token`) masked the bug — there was no bill to notice it against.