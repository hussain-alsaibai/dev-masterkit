# Bounty Freeze Detection

> Detect frozen/resolved/stale bounties before wasting implementation effort.

## When to Use

Before starting bounty implementation work, run through this checklist. A frozen bounty
is one where the maintainers have explicitly or implicitly stopped accepting new PRs.

## Hard-Freeze Detection (skip immediately)

Run these checks first. Any single hit = hard freeze = SKIP.

### 1. Closed competing PRs referencing the issue

```
gh pr list --state closed --search "<issue-title-or-keyword>" --repo <owner/repo> --json number,title,body,closedAt,mergeableState
```

Look for PRs with:
- Body or title referencing the issue number
- `closedAt` within 90 days
- `mergeableState` == "unstable" or "behind" (merged/closed, not stale)

If a PR was closed/merged within 90 days and the issue is still open, the issue may be
frozen-in-place while the PR undergoes review.

### 2. Issue body freeze language

Read the issue body. Reject if any of these patterns appear (case-insensitive):

| Pattern | Meaning |
|---------|---------|
| `do not submit` | Maintainer explicitly asked to stop |
| `finalized` | A PR has been selected |
| `kindly refrain` | Maintainer request to pause |
| `pending review` | Selected PR in review |
| `pending app review` | External app store review step |
| `PR #N has been finalized` | Specific PR named |
| `please do not open new PRs` | Explicit block |

### 3. Issue state reason = "REOPENED"

Check `gh issue view <num> --json stateReason`. If `stateReason == "REOPENED"` and the
last 5 comments are all from non-maintainers, the issue was reactivated without
maintainer buy-in — high risk of freeze.

## Soft-Freeze Detection (escalate to analyst)

These are risk factors. Escalate if 2+ apply.

### 4. Competing PRs > 20

```
gh pr list --state open --search "<issue-title>" --repo <owner/repo> --json number,title,createdAt | wc -l
```

>20 open PRs with no recent (30d) merges suggests the queue is saturated. Maintainers
may have quietly stopped reviewing. Flag as `SATURATED` — low ROI.

### 5. Last maintainer comment > 30 days ago

```
gh issue view <num> --json comments --jq '.comments[] | select(.authorAssociation == "MEMBER" or .authorAssociation == "OWNER") | {createdAt, body}' | head -20
```

No maintainer comment in 30+ days on a bounty issue = maintainer moved on. Not a hard
rejection, but high risk of PR sitting unreviewed.

### 6. Bounty-labeled issues with > 50 comments

High comment count without resolution suggests an unresolvable disagreement or scope
creep. Check last 3 comments for maintainer signals.

## Decision Matrix

```
┌─────────────────────────────────────┬────────────┐
│ Condition                           │ Action     │
├─────────────────────────────────────┼────────────┤
│ Hard-freeze hit                     │ SKIP       │
│ Competing PRs > 20                  │ SKIP/LOW-ROI │
│ Maintainer said "do not submit"     │ SKIP       │
│ Selected PR pending review          │ SKIP       │
│ > 2 soft-freeze factors             │ DEFER      │
│ Fresh (no signals)                  │ PROCEED    │
└─────────────────────────────────────┴────────────┘
```

## Verified Cases

| Date | Issue | Result |
|------|-------|--------|
| 2026-08-02 | activepieces#8072 `[MCP] Gmail` | FROZEN — "PR #8083 finalized, pending App Review" in issue body |
| 2026-08-02 | arakoodev/EdgeChains#273 Qdrant | SOFT-FROZEN — 66 competing PRs, no recent merges, PAT-blocked anyway |
| 2026-08-02 | arakoodev/EdgeChains#279 Palm2 | SOFT-FROZEN — 25+ competing PRs |

## Workflow Integration

Add as a mandatory pre-check gate in the bounty-scanner workflow:

```
Bounty selected → Run freeze detection → [FROZEN] → Log reason → Skip
                                                → [SOFT]   → Log risk factors → Analyst review
                                                → [FRESH]  → Proceed
```

Last verified: 2026-08-05
