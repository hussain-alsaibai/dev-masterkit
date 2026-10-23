# tiny-bounty-queue Guide

## Repo
https://github.com/hussain-alsaibai/tiny-bounty-queue

## One-liner
Zero-dependency bounty issue queue with pluggable scoring and dispatch.
Pure Python stdlib. MIT.

## Status
**Repo does not exist upstream yet** (`https://github.com/hussain-alsaibai/tiny-bounty-queue`
-> HTTP 404, checked 2026-10-23). Local clone only.

## Last Verified
2026-10-23

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
```python
from tiny_bounty_queue import Queue, Scorer, parse_github_issue

issue = parse_github_issue(raw_issue_json)
scorer = Scorer()
scored = scorer.score(issue)

q = Queue()
q.add(scored)
print(q.next())
```

## Key Features
- Per-issue scoring with a transparent breakdown
- Filter rules for rejecting ineligible issues
- Dispatch layer separate from scoring
- 18 tests passing (verified by run, 2026-10-23)

## Related
- `tools/tiny-bounty-guide.md` — target tracking CLI
- `tools/tiny-bounty-workflow-guide.md` — end-to-end workflow with anti-scam filters
