# A Model Override Disables The Whole Fallback Chain

**A rule for any scheduled job, worker, or sub-agent that pins a model.**

> Found 2026-11-02 while a 7-entry, 5-provider fallback chain was healthy and
> three jobs were still failing in under one second. **Last verified:**
> 2026-11-02 — the runtime source was read directly, all four per-job
> overrides were cleared, and the previously failing job then completed
> **OK in 18.5s**.

## The Rule

> **A fallback chain only helps jobs that do not pin a model. A per-job
> override is not a preference; it is a decision to have no fallback at all.**

The runtime says so itself:

```
if (modelFallbackAvailability.kind === "disabled_by_model_override")
  log.warn("[model-fallback] configured fallbacks disabled by user model override ...")
```

A job with `payload.model` set gets **no fallback**. It was pinned to
`google/gemini-3-flash-preview` and died on Google's 429 quota error with
nothing to catch it — while a healthy chain sat in the config, unused.

**Six of 32 jobs were pinned** and failed with Google 429 *"exceeded your
current quota"*.

## Three Failure Classes, None Of Them A Provider Outage

### 1. An alias in `payload.model` is checked against the allow-list as a model id

```
automation model override 'flash' rejected by agents.defaults.modelPolicy.allow:
minimax/flash is not in [deepseek/deepseek-chat, google/gemini-3-flash-preview, ...]
```

The allow-list holds **full model ids**. The job held the **alias** `flash`.
The alias no longer existed in the model's alias set (the config had been
rebuilt the day before, and the alias set changed), so the override never
resolved to a concrete model and the preflight rejected it.

**Rule: `payload.model` must be a full `provider/model` id, not an alias
name.** The listing command prints the Model column truncated — check the job
detail view for the real value.

### 2. A one-second failure naming a policy is a config mismatch

Provider outages produce latency and retry text. **"rejected by
modelPolicy.allow" means the string never matched.** A failure in under a
second with a policy name in it is a config mismatch, and chasing the provider
will find nothing there.

### 3. The provider timeout is not the job timeout

```
models.providers.minimax.timeoutSeconds = 300
```

Four consecutive failures at **exactly 300s**, on a job whose own timeout was
already 900s. The phase in the error message is the discriminator:

| phase in the error | means |
|---|---|
| `model-call-started` | the **provider** ceiling |
| `tool-execution-started` | the **job** timeout |

Lower the provider timeout so a slow rejection fails fast. A legitimate call
to that provider takes 0.5-3s; 300s of ceiling only ever truncates a call that
was never going to succeed. **A provider that hangs for two minutes and then
says 429 is worse than one that says 429 immediately.**

## The Procedure

1. **List every job's model override.** Find the pinned jobs; they are the
   ones the chain is not protecting.
2. **Clear the overrides** unless there is a specific reason to keep one.
   The chain exists precisely for the jobs nobody is watching.
3. **Write the config before triggering a test run.** A config change
   invalidates in-flight run authority — runs that span the write are
   interrupted, which looks like a failure of the thing you just fixed.
4. **Verify with an actual run, not with a diff.** A diff proves the string
   is right. A run proves the job works.

```bash
# Prove a job works after the change
openclaw cron run <job-id>
```

## The Verification That Actually Proves It

The same job, three different runs, three different causes:

```
00:00:04  error   0.2s   override 'flash' rejected by modelPolicy.allow
01:25:51  error 602.4s   timed out (model-call-started) — fallback walk
01:37:23  ok     19.3s   no error
```

**The latest error alone would have sent you down the wrong path twice.** The
second run failed even though the fallback *worked* — the log showed
`candidate_failed` on the primary and `candidate_succeeded` on the fallback.
The chain did its job and the job still died, because the fallback walk
consumed the remaining budget. The next identical run took 19.3s, because the
429 storm had passed.

**Rule: a job timeout is not a verdict on the implementation.** Read the run
history, not just the newest error.

See also `prompts/fallback-chain-needs-a-live-probe.md` (the chain must be
alive before it can help) and `prompts/cron-stagger-rpm.md` (avoiding
synchronized bursts in the first place).
