# A Re-Sent Token Total Is Not A Request

**Last verified:** 2026-11-22 (microsoft/TokenEconomizer#316 OPEN + MERGEABLE,
verified with `gh pr view 316`; reproduced locally against `1bfeccd`, red phase
2 of 4 tests)

## The prompt

> You are auditing a usage/cost ledger that counts one "request" per event
> carrying a cumulative token total. Before you trust that count:
>
> **1. A cumulative counter is idempotent; a request is not.** If the source
> emits snapshots of a running total, the count of *events* is not the count of
> *model calls*. Ask what produces the total, not how often it is written.
>
> **2. `total_token_usage` moves only when a model call happens.** That makes it
> the right key. A rate-limit snapshot, a post-compaction local estimate, and a
> usage-limit error all carry a total — none of them has a call behind it.
>
> **3. "Identical to the previous event" is the wrong guard.** A compaction can
> land between a call and the re-send of that call's totals, so the re-send is
> *not* adjacent. Compare against the **set of totals already seen**, not the
> last one.
>
> **4. Compare on the counters that can move, not on the whole payload.** Reduce
> the snapshot to the numeric fields a call changes. A harmless extra field
> otherwise registers as a new request, which is the same bug in the other
> direction.
>
> **5. The last cumulative total still wins for the breakdown.** Dedupe the
> *count*; do not discard the *latest* snapshot — it is the state the session
> actually reached.

## What happened (2026-11-22)

`microsoft/TokenEconomizer` issue #299: `codex_session_usage` counted one
request per `token_count` event carrying `total_token_usage`. Codex re-sends
totals it already has and persists those events in the rollout:

- `update_rate_limits` → `send_token_count_event` (a compaction's rate-limit
  snapshot, and a usage-limit error);
- `recompute_token_usage` (the local estimate after compaction), which replaces
  `last_token_usage` only and emits the event again.

Neither has a model call behind it. The ledger and `te status` reported **5
requests for a 3-request session**. Fixed in PR #316 by
`tokeneconomizer/trace/codex.py` with a seen-totals set plus a `_usage_key`
reduction over the numeric counters.

Measured here on the issue's rollout:

```
before: requests: 5
after:  requests: 3
```

Four regression tests in `tests/test_trace.py`, 2 failing on `1bfeccd`. The
adversarial one is a re-sent total arriving **after** a later call — the case a
previous-event comparison gets wrong and therefore accepts.

## Why the previous-event guard looks right and is not

The tempting fix is `if event == last_event: skip`. It passes the reporter's
reproduction, because in that rollout the duplicates are adjacent. It fails the
moment a compaction or a rate-limit update interleaves, and nothing in the
issue's reproduction exercises that ordering. **A dedupe key must be a property
of the value, not of its position in the stream.**

## Reporting honestly

The PR body states the 4 pre-existing `experiments/` failures instead of
claiming a clean suite. A contribution that reports "all green" while the tree
is red is the thing a maintainer cannot verify without doing your work.

## Last verified

2026-11-22 — `gh pr view 316 --repo microsoft/TokenEconomizer` → OPEN,
MERGEABLE, author `hussain-alsaibai`, head `fix/codex-resent-token-count`.
