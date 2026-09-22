# tiny-bounty-queue Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-bounty-queue
**Last verified:** 2026-09-22
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

Score, filter, queue, and dispatch GitHub bounty issues from Algora, Opire, Gitcoin, and label-based OSS bounties. Deterministic scoring formula, anti-scam defaults, and auditable dispatch order. Built for autonomous coding agents that need to decide *which issue to work next, in what order, under what budget*.

## When to use

An autonomous agent or cron that crawls bounty boards and wants a deterministic, auditable way to pick the next issue. Replaces ad-hoc shell scripts and spreadsheets.

## Quick start

```python
from tiny_bounty_queue import BountyQueue, Score

q = BountyQueue()
q.add(issue)                          # scored automatically
top = q.top(n=5)                      # top 5 by score, anti-scam filtered
for issue in top:
    dispatch(issue)                   # work in order
```

## Key features

- **Deterministic score formula** — same input → same rank
- **Anti-scam defaults** — filter obvious low-quality / dead / duplicate bounties
- **Multi-source** — Algora, Opire, Gitcoin, GitHub labels
- **Budget-aware dispatch** — refuses to over-claim
- **Single file** — auditable in one sitting

## Integration pattern

Pair with `tiny-bounty-workflow` (full workflow with PR, review, merge) and `tiny-bounty` (issue board scraper). The queue decides *what*; the workflow decides *how*.

## Notes

- Created 2026-09-22 as part of the tiny-* ecosystem
- MIT licensed, zero dependencies
- Tests + examples in `tests/` and `examples/`
