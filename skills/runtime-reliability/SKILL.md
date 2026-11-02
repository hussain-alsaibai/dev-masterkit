---
name: runtime-reliability
description: "Audit a scheduled-job runtime for the failure classes that hide behind plausible error messages: dead fallback entries, model overrides that disable the chain, retries that burn budget on impossible requests, stale error counters mistaken for live failures, and dead credentials named in job prompts. Use when jobs fail intermittently, when a healthy-looking config produces failures, or when a scheduled task fails for a different reason each time it runs."
---

# Runtime Reliability

**Use when:** a scheduled job or worker fails intermittently; a fallback chain
is configured and healthy-looking but jobs still die; the same job fails for a
different reason each time it runs; a dashboard shows errors that are not
reproducing; or a job's prompt mentions a credential.

**Do not use when:** the error names a file and line of code you wrote. That is
a code defect, and `skills/dev-env-defects/SKILL.md` tells you how to triage
it.

**Last verified:** 2026-11-02 - every fact below was reproduced on this host.
A 7-entry, 5-provider chain was probed entry by entry; 4 registered
OpenRouter models answered 503/404; 4 per-job model overrides were cleared;
49 HTTP 400s were reclassified; 3 dead-credential job prompts were found with
one grep; and the job that had failed in 0.4s completed OK in 18.5s after the
fix.

## The Core Rule

> **Read the run history before you change anything. The latest error alone
> will send you down the wrong path.**

One job, three runs, three distinct causes:

```
00:00:04  error   0.2s   override 'flash' rejected by modelPolicy.allow
01:25:51  error 602.4s   timed out (model-call-started) - fallback walk
01:37:23  ok     19.3s   no error
```

The second failure is the one that misleads. The log showed the fallback
**working** - `candidate_failed` on the primary, `candidate_succeeded` on the
fallback - and the job still died, because the walk consumed the remaining
budget. Fixing the third run's cause would have changed nothing.

## Procedure

### 1. Read the receipts, not the counter

```sql
select job_id, status, started_at_ms, finished_at_ms, error_text
from cron_run_receipts
order by started_at_ms desc
limit 40;
```

Read it as a table. `consecutiveErrors` survives between runs, so 9 errors
may describe a run that happened yesterday.

**The duration is part of the diagnosis:**

| duration | class |
|---|---|
| under 2s | config mismatch, preflight rejection, missing file |
| exactly the provider timeout | the provider ceiling, not the job timeout |
| exactly the job timeout | the budget ran out |

The phase in `error_text` is the most useful word in it:
`model-call-started` means the provider hung; `tool-execution-started` means
the job ran out of budget.

See `prompts/a-stale-error-counter-is-not-a-live-failure.md`.

### 2. Probe every fallback entry with a real completion

A config read proves nothing. `openclaw models list` prints `configured` for
entries that cannot be called.

```bash
curl -s -w '\n%{http_code}' \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"model":"<id>","max_tokens":64,"messages":[{"role":"user","content":"Reply with exactly: OK"}]}' \
  https://<endpoint>/v1/chat/completions
```

Rules for the probe itself:

- `max_tokens >= 64`. At 16, two live models returned `content: None` and
  looked dead.
- **Probe twice.** One entry answered 429 on one of two probes.
- Record the status, not just the body.

**Also check registration.** `models: []` under a provider is a silent killer:
the chain lists the model, the alias resolves, and every failover dies
instantly. In one 4-hour window that dead first hop failed **26 times**.

**Count providers, not entries.** Three minimax models are one provider with
three doors.

See `prompts/fallback-chain-needs-a-live-probe.md`.

### 3. Find the per-job model overrides

```bash
openclaw cron list          # the Model column is truncated
openclaw cron show <id>     # read the real value
```

A job with `payload.model` set gets **no fallback at all** - the runtime says
`modelFallbackAvailability.kind === "disabled_by_model_override"`. Six of 32
jobs were pinned and died on one provider's quota error while a healthy chain
sat unused.

**`payload.model` must be a full `provider/model` id.** The allow-list holds
full ids; an alias like `flash` is rejected in 0.4s with a policy name in the
message. **A one-second failure naming a policy is a config mismatch, not a
provider outage.**

See `prompts/a-model-override-disables-the-fallback-chain.md`.

### 4. Classify failures by status code, not by reason string

A context-length overflow (666,035 tokens against a 512,000-token window) was
retried **8 times** as `reason=timeout`. Every retry sent the same oversized
request and got the same 400.

**A context-length 400 is not retryable.** Neither is 401, 403, or 422.

And the status has to survive to reach the classifier. `curl -sf` discards the
body on a non-2xx, so the caller sees `command failed` and nothing else - a
backoff rule written as `/403|rate limit/` never matches, and **every failure
is classified as 'not a rate limit'**.

```bash
# RIGHT: status on the last line, body preserved
curl -s -w '\n%{http_code}' ...
```

**A band that is dropped must be dropped for a recorded reason.** Log the
status next to the drop.

See `prompts/classify-by-status-code-not-by-reason-string.md`.

### 5. Grep for dead credentials named in prompts

When a credential dies, every prompt that names it becomes a landmine.

```bash
grep -rn "GitHUB_PAT" ~/.openclaw/cron/ ~/.openclaw/openclaw.json \
  ~/.openclaw/workspace/ 2>/dev/null
```

That one command found all three affected job prompts. **The fix is not to
remove the reference - it is to name the dead credential as dead in the
prompt**, so the next agent does not rediscover it:

```
Use the token from the gh CLI credential store (`gh auth token`).
The `GitHUB_PAT` env var is a DEAD token and returns HTTP 401. Do not use it.
Last verified: 2026-11-02 - `gh auth token` returned HTTP 200 on this host.
```

Prove it before writing it down:

```bash
git -c http.extraheader="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$(gh auth token)" | base64 -w0)" \
    push --dry-run origin main
```

A dry run distinguishes 'auth failed' from 'nothing to push' in one command.

See `prompts/a-dead-credential-named-in-a-prompt-fails-every-run.md` and
`prompts/credential-order-is-not-validity.md`.

### 6. Check `/tmp` before blaming the tool

```bash
df -h /tmp
```

A full `/tmp` produces `ENOSPC` **in the middle of a successful operation** -
while writing web-fetch spill logs - and it reads like a fetch failure. The
spill files are never rotated. Check before every multi-step run; check
`ps` before deleting any directory.

See `prompts/check-tmp-space-before-any-multi-step-run.md`.

### 7. Verify the fix with an actual run

**A diff proves the string is right. A run proves the job works.**

```bash
openclaw cron run <job-id>
```

The job that had failed in 0.4s completed **OK in 18.5s** after the override
was cleared. A config diff would have shown the right string and proven
nothing.

**Write the config before triggering the test run.** A config change
invalidates in-flight run authority - a run that spans the write is
interrupted, which looks like a failure of the thing you just fixed.

## The Reporting Rule

> **Report the number that changed.** 'health-monitor-check: 0.4s failure ->
> OK in 18.5s' is a report. 'Fixed the model override' is a claim.

And when the honest answer is that the fallback worked and the job still
died, say that:

> The chain walked correctly - primary failed, fallback succeeded - and the
> job still exceeded its budget. The budget, not the chain, was the defect.

## Related

- `prompts/fallback-chain-needs-a-live-probe.md`
- `prompts/a-model-override-disables-the-fallback-chain.md`
- `prompts/classify-by-status-code-not-by-reason-string.md`
- `prompts/a-stale-error-counter-is-not-a-live-failure.md`
- `prompts/a-dead-credential-named-in-a-prompt-fails-every-run.md`
- `prompts/check-tmp-space-before-any-multi-step-run.md`
- `skills/cron-orchestrator/SKILL.md` - creating the jobs this skill audits
- `skills/dev-env-defects/SKILL.md` - when the error names your code
