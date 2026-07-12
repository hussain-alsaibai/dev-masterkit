# bounty-saturation-pat-blocked-skip - Preserve time when the queue is saturated and PRs are blocked

## Description

Use this decision prompt during bounty-scanner runs when the highest-ranked
issues are all saturated and the current GitHub credential still cannot open
cross-fork upstream PRs. In that state, the correct output can be **no new
implementation**: record the scan, explain the skip, keep any previously
parked branches visible, and wait for either a fresh low-competition target
or a PAT scope fix.

This is the companion to `bounty-saturation-resolved-not-skip.md`. That prompt
explains when to override saturation and ship anyway. This one explains when
not shipping is the productive choice.

## Trigger

Apply this prompt when all of the following are true:

1. The top official bounty candidates all have multiple open PRs, stale review
   queues, or content-farm signals.
2. At least one already-implemented branch is parked on a fork because the bot
   PAT cannot create upstream PRs.
3. The new candidate would likely produce another parked branch rather than a
   mergeable PR.
4. There is no clear mirror-shape override like the Qdrant case from
   `bounty-saturation-resolved-not-skip.md`.

If any one of those is false, continue normal bounty triage.

## Decision Rule

```
if all_top_candidates_are_saturated
   and cross_fork_pr_creation_is_still_blocked
   and no_candidate_has_a_verified_low-effort_override:
       do_not_implement_new_code
       write a traceable skip report
       carry forward the existing parked-branch handoffs
else:
       continue normal verification and implementation
```

This is not a pessimism rule. It is a throughput rule. A parked branch has
value when there is a credible path to PR creation or when the implementation
itself teaches a reusable pattern. A second or third parked branch behind the
same credential blocker usually adds inventory, not leverage.

## What to Record

For a skipped run, capture:

- scan size and source count (official issues, bounty labels, rejected farms)
- top candidates with payout, open PR count, and rejection reason
- current parked branches and SHAs that are still waiting on PAT scope
- the exact blocker, usually `403 Resource not accessible by personal access token`
- one concrete scanner improvement if the run exposed a scoring problem

Do not create a fake prompt, skill, tool, or repo update just to make the day
look non-empty. The skip report itself is the artifact when it preserves
future decision quality.

## Scanner Improvement Pattern

If every top candidate bottoms out at the same competition score, the scanner
is no longer ranking useful work. Add a follow-up item to surface either:

- lower-scoring candidates with zero open PRs, or
- saturated candidates with an explicit `saturated_warning` so humans can see
  why a high payout is still not actionable.

The goal is not to hide saturated issues; it is to separate "popular but still
worth doing" from "popular and operationally blocked."

## Last verified: 2026-07-12

- Daily bounty run scanned 200 official issues and 327 bounty-labeled issues,
  rejected 10 bounty-farm/scam candidates, and analyzed 7 top candidates.
- All top candidates had at least 2 active PRs or stronger saturation signals.
- Existing parked branches remained blocked by fine-grained PAT scope:
  `hussain-alsaibai/EdgeChains:ts` at `d0ceb72a` and
  `hussain-alsaibai/gitea:feat/commit-inline-comments-4898` at `c50dffec5a`.
- Result: no new fork, no new commits, no PR API calls. The durable lesson was
  the explicit skip gate above plus a scanner follow-up to surface
  zero-open-PR candidates even when their raw score is lower.
