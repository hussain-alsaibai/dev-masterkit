# tiny-bounty-queue Guide

## Repo
https://github.com/hussain-alsaibai/tiny-bounty-queue

## One-liner
Zero-dependency bounty issue queue with pluggable scoring and dispatch.
Pure Python stdlib. MIT.

## Status
**Live upstream as of 2026-11-02.** The repo was created on GitHub at
17:10 UTC on 2026-11-02, *after* this guide's earlier same-day 404 re-check.

`GET /repos/hussain-alsaibai/tiny-bounty-queue` -> **HTTP 200**, MIT, default
branch `main`, `tiny_bounty_queue.py` + `tests/` + `examples/`.

```bash
pip install git+https://github.com/hussain-alsaibai/tiny-bounty-queue.git
```

## Last Verified
2026-11-02 - cloned from upstream and ran the suite: **18 passed** (matches
the count this guide already claimed).

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_bounty_queue import
BountyQueue, Score`. **Neither name exists.** Verified against the local clone:

```
BountyIssue, ScoreBreakdown, ScoredBounty, QueuedBounty,
Filter, Scorer, Queue, Dispatch, parse_github_issue, to_json
```

The queue is **`Queue`**, the scoring engine is **`Scorer`**, and the score
decomposition is **`ScoreBreakdown`**. `BountyIssue` is the raw issue,
`ScoredBounty` / `QueuedBounty` the scored forms, `Filter` the rejection
rules, and `Dispatch` the action layer.

## Quick Example
Executed against upstream on 2026-11-02 (output pasted from the run).

```python
from tiny_bounty_queue import BountyIssue, Scorer, Filter, Queue, Dispatch

agent_profile = {"python": 0.9, "go": 0.5, "qdrant": 0.4,
                 "webhooks": 0.7, "docs": 0.95}
scorer = Scorer(capability=agent_profile)
flt = Filter(blocked_phrases=("seed phrase", "send me your"),
             max_age_hours=24 * 60, forbid_repos=frozenset({"scam/repo"}))
queue = Queue(scorer=scorer, flt=flt, max_concurrent=1, budget_usd=300.0)

issues = [
    BountyIssue(id="arakoodev/EdgeChains#273", repo="arakoodev/EdgeChains",
                number=273, title="feat: Qdrant adapter", reward_usd=50.0,
                required_skills=frozenset({"python", "qdrant"}), age_hours=6.0),
]
plan = Dispatch(queue).plan(issues, agent_profile)
print(Dispatch(queue).explain(plan))
```

```
Dispatch plan: 1 items, $5.00 est.
  [00] arakoodev/EdgeChains#273  $50 score=0.779 cap=0.65 fresh=0.94 lock=1.00
```

**Three API corrections found by running it on 2026-11-02** (the previous
snippet in this guide used all three wrong):

1. `Scorer()` needs **`capability=`**; `Queue()` needs **`scorer=`** - the
   zero-argument forms in the old snippet raise at construction.
2. **`Queue` has no `add()` and no `next()`.** Its surface is `admit(issues)`
   (an *iterable*, returning `(kept, dropped_with_reason)`) plus the
   constructor fields `budget_usd`, `max_concurrent`, `estimated_cost_per_issue_usd`.
3. **`parse_github_issue(repo, number, title, body, ...)` takes positional
   arguments, not a raw issue dict.** And dispatch is
   **`Dispatch(queue).plan(issues, agent_profile)`** - `plan()` requires the
   issue iterable, it does not read a pre-filled queue.

## Key Features
- Per-issue scoring with a transparent breakdown
- Filter rules for rejecting ineligible issues
- Dispatch layer separate from scoring
- 18 tests passing (verified by run, 2026-10-23)

## Related
- `tools/tiny-bounty-guide.md` — target tracking CLI
- `tools/tiny-bounty-workflow-guide.md` — end-to-end workflow with anti-scam filters
