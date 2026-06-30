# cron-stagger-rpm — Prompt for Avoiding Synchronized Model RPM Bursts

## Description

Steers an agent diagnosing recurring cron job failures ("429 rate limit exceeded (RPM)")
to add `staggerMs` jitter to overlapping schedules. Prevents the common trap of
multiple jobs firing on the same minute and bursting the model provider's rate limit.

## The Prompt

```
Multiple cron jobs are failing with "429 rate limit exceeded (RPM)" or similar
provider rate-limit errors. Diagnose and fix:

1. **Find the synchronized jobs.** List all cron jobs:
     - `cron list` (OpenClaw) or equivalent
   Look for jobs sharing the same minute field, e.g. all firing at `0 21 * * *`
   (every job at 21:00 sharp).
2. **Quantify the burst.** Count jobs firing within the same 60s window. If you
   see 5+ jobs all on `0 21 * * *`, you have a burst of N agentTurns calling
   the model provider at the same instant.
3. **Apply stagger.** Add `staggerMs` to the schedule:
     ```json
     {
       "schedule": {
         "kind": "cron",
         "expr": "0 21 * * *",
         "tz": "Asia/Bahrain",
         "staggerMs": 45000  // 30-90s typical; pick unique values per job
       }
     }
     ```
   Different jobs should have different stagger windows so they don't just
   shift the problem by N seconds — they should spread across minutes.
4. **Verify precedence is preserved.** A 9:00 AM sharp job should still
   semantically be "9 AM". If you must stagger past the exact minute, document
   it in the job's `description`.
5. **Watch the next 24h.** Confirm the 429 errors drop. If a different
   provider has a per-minute limit, you may need `staggerMs` up to 60000.

Reporting:
- Show before/after cron list with stagger values.
- Note which jobs are most expensive (largest prompts, biggest context) and
  stagger those first.
- Add a "stagger policy" note to the cron-orchestrator skill.

Alternative: if you cannot add staggerMs to the scheduler, insert a
`sleep $((RANDOM % 60))` at the top of the job's script body. Less clean,
but works as a quick mitigation.
```

## When to Use

- Recurring 429 rate limit errors on cron-triggered agent jobs
- All cron jobs share the same minute field
- Provider RPM (requests per minute) is a tighter constraint than TPM
- Adding new cron jobs that would increase burst load

## Last Verified: 2026-06-30