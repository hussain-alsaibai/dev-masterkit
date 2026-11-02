# A Stale Error Counter Is Not A Live Failure

**A rule for reading a health dashboard, a job status table, or any counter
that survives between runs.**

> Found 2026-11-02. Eight of nine jobs showing errors had **last run on
> 2026-11-01** at slots between 16:00 and 21:00 UTC, and had not fired since.
> **Last verified:** 2026-11-02 — the receipt table was read directly and the
> run timestamps confirmed the counters were describing runs that had already
> finished.

## The Rule

> **Before acting on an error counter, check the job's last receipt
> timestamp. A counter that survives between runs is a statement about the
> past, not about now.**

## The Failure

A status view reported:

```
job                       consecutiveErrors
daily-evolution-report     9
daily-log-init             7
daily-repo-discovery       4
...
```

Nine consecutive errors reads like something is broken right now. It was not.
Those nine were **nine errors on the last run**, which happened the previous
day. The jobs had not run since. Reading the counter as a live failure sends
you chasing a bug that is not running — and, worse, sends you *changing a
configuration that is currently working*.

## The Two Questions To Ask First

1. **When did it last run?** If the last run was before your last fix, the
   counter predates the fix.
2. **Did it run after your last fix, and how did it end?** That is the only
   number that describes the current state.

## Reading The Receipt History

The receipts are the real source of truth. They are per-run records with a
start time, a duration, a status, and an error text:

```sql
select job_id, status, started_at_ms, finished_at_ms, error_text
from cron_run_receipts
order by started_at_ms desc
limit 40;
```

Read it as a table, not as a count. A single job's history tells you more
than any dashboard:

```
00:00:04  error   0.2s   override 'flash' rejected by modelPolicy.allow
01:25:51  error 602.4s   timed out (model-call-started) — fallback walk
01:37:23  ok     19.3s   no error
```

**Same job. Three causes. Three different fixes.** The latest error alone
would have sent you down the wrong path twice — once for the policy
mismatch, once for the timeout. Only the history shows that the second
failure was a *different* defect from the first.

## The Rule About Error Text

**`error_text` carries the reason; the duration carries the class.**

| signal | what it tells you |
|---|---|
| failed in < 2s | config mismatch, preflight rejection, or a missing file |
| failed at exactly the provider timeout | the provider ceiling, not the job timeout |
| failed at exactly the job timeout | the budget ran out |
| failed with a 4xx | the request was wrong; retrying proves nothing |
| failed with a 5xx | the server was wrong; retrying is reasonable |

The phase in the error message is part of the text, and it is the most
useful word in it: `model-call-started` vs `tool-execution-started` is the
difference between "the provider hung" and "the job ran out of budget".

## Reading The Live State

Where the runtime keeps its job state, read it **read-only and in place** —
do not copy the database out and do not open it with a tool that locks it:

```python
import sqlite3
con = sqlite3.connect(
    'file:/path/to/state/openclaw.sqlite?mode=ro', uri=True
)
rows = con.execute(
    "select job_id, status, started_at_ms, finished_at_ms, error_text "
    "from cron_run_receipts order by started_at_ms desc limit 40"
).fetchall()
```

Two runtime details worth knowing:

- The job table carries `state_json` (`consecutiveErrors`, `lastDiagnostics`,
  `runningAtMs`) and `job_json` (payload, schedule, delivery).
  `state_json.lastDiagnostics.summary` is the only place per-hop failure
  reasons live.
- A legacy on-disk job file may be **stale** after a migration. The live
  state database is the source of truth; the legacy file is not.

See also `prompts/classify-by-status-code-not-by-reason-string.md` (reading
the failure class) and `prompts/a-model-override-disables-the-fallback-chain.md`
(three causes, one job, three fixes).
