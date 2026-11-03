# Quota Exhaustion Is Not A Throttle

**A rule for any retry policy, fallback chain, or backoff keyed on a provider
error label.**

> Found 2026-11-03. A daily job carried **8 consecutive errors** and a
> `lastDurationMs` of **2,571,414** (42.8 minutes). Every attempt burned the
> whole multi-hop chain before failing. **Last verified:** 2026-11-03 — the
> stored diagnostics were read out of the live cron state DB and the message
> body confirmed.

## The Rule

> **One HTTP status code and one error label can carry two failures with
> opposite correct responses. Split them before you retry.**

## The Evidence

The job's stored diagnostic:

```
summary: "⚠️ Token Plan usage limit reached: Upgrade your Token Plan or
          purchase Credits for more usage. (2056)"
lastErrorReason: "rate_limit"
```

Two different things:

| | provider message | correct response |
|---|---|---|
| **transient throttle** | "The AI service is temporarily rate-limited. Please try again in a moment." | **retry**, with backoff |
| **plan exhausted** | "Token Plan usage limit reached ... (2056)" | **stop**, and escalate |

Both arrive as HTTP 429. Both are stored as `rate_limit`. The runtime's
summary field keeps the label; **the body is the only thing that
distinguishes them.**

**A retry policy keyed on the reason retries a depleted plan forever.**
Eight runs burned 42.8 minutes to produce the same 429.

## The Procedure

1. **Read the body, not just the label.** The numeric/code suffix inside the
   message is the discriminator. `2056` means the plan is spent.
2. **Match on the specific marker first**, then fall back to the generic
   class:

```javascript
function classify(err) {
  const body = String(err?.body ?? err?.message ?? '');
  if (/Token Plan usage limit|\(2056\)/i.test(body)) return 'quota_exhausted'; // stop
  if (err?.status === 429) return 'throttled';                              // retry
  if (err?.status === 400 && /context|token limit|too long/i.test(body)) {
    return 'impossible';  // a context-length 400 is not retryable
  }
  return 'unknown';
}
```

3. **Make the exhausted case non-retryable.** A quota death should raise a
   distinct, visible error that says *the plan is depleted*, not *rate
   limited*.
4. **A single provider in every fallback hop is a chain of mirrors.** The same
   failed job reported `All models failed (4)` with four `rate_limit`
   reasons: `minimax/MiniMax-M3`, `minimax/M2.7-highspeed`,
   `minimax/M2.5-highspeed`, `gemini-3-flash-preview`. **Three of the four are
   literally the same plan.** The fourth is the one provider that has been
   429-ing daily. A walk across four entries that share one quota does not
   add a door - it repeats the same locked door.

## Why The Chain Walk Made It Worse

Every hop ran to completion, every hop failed on the same exhausted plan,
and the total budget was consumed 4 times over. **Fallback is for
independent failure modes.** Hops that share a quota, a network path, or a
credential are one failure mode wearing four names.

The fix is structural, not a retry tweak: move the scheduled jobs to a
provider that bills per-token or has spare quota, so a plan limit degrades
one job instead of killing the stack.

## The Generalisation

This is the same shape as a context-length 400 (not retryable - see
`prompts/classify-by-status-code-not-by-reason-string.md`) and an
authentication failure (not retryable - see
`prompts/a-dead-credential-named-in-a-prompt-fails-every-run.md`).
**Before retrying a classified failure, ask: could a retry possibly succeed?
If the answer is no, the retry is pure cost.**
