# An Assigned Issue Is a Taken Issue

**A selection rule for any agent that picks work from a public issue tracker.**

> Found 2026-10-25 while the daily bounty scanner selected
> `pipeshub-ai/pipeshub-ai#4063` — an issue a maintainer had already assigned to
> `louisss1016`, with an open PR (#4068) behind it. The issue body said
> *"Comment here to claim it. One assignee."* The scanner read that sentence and
> moved on. **Last verified:** 2026-10-25 (scanner.js + daily-bounty-work.js +
> `test-assigned-issues.js`, 11 checks passing)

## The Blind Spot

A scanner for open work usually checks every signal *except* the one that
decides whether the task is still open:

| Signal | Checked? | Cost |
|--------|----------|------|
| Label (`good first issue`, `help wanted`) | yes | free |
| Body shape (`How to verify`, acceptance criteria) | yes | free |
| Star count / fork ratio | yes | 1 API call |
| Closed / frozen | yes | free |
| Scam fingerprint (same-day account, bait body) | yes | free |
| Competing open PRs | yes | 1 API call |
| **Assignee** | **NO** | **free** |

The assignee field is the claim. If someone is assigned, the task is not
available, no matter how well it scores, how much it pays, or how few
rivals it has.

## Why It Was Missed

Both components that gate the work read the same issue object and both
looked at the wrong properties:

- `scanner.js` decided what to *shortlist* — it checked labels, body shape,
  competition, scam signals.
- `daily-bounty-work.js` decided what to actually *start* — it re-checked
  nothing that had not already been checked.

So the same omission existed in both places, and neither was a bug: each
component did exactly what it was written to do. **A rule that is absent
from every layer is invisible to every layer.**

## The Fix

The GitHub search API returns `assignees` (an array) on **every** issue
object it returns. It costs **no extra request** — it is already in the
payload you are parsing.

```javascript
// scanner.js — shortlist stage
if (issue.assignees && issue.assignees.length > 0) {
  return reject(issue, "already_assigned");
}
// some payloads carry the singular form
if (issue.assignee) {
  return reject(issue, "already_assigned");
}
```

```javascript
// daily-bounty-work.js — work-start stage
if (candidate.assignees?.length || candidate.assignee) {
  log("[SKIP] already assigned:", candidate.number);
  return null;
}
```

**Check it in both.** The shortlist is where ranking happens; the work-start
stage is where time is spent. Fixing only one leaves the other as the path
that matters.

## The Ordering Rule

Check the assignee **before** the competition count. Both are free signals
from the same payload, but they answer different questions:

- competition = *how many* rivals
- assignee = *whether anyone already claimed it*

One rival whose PR is merged is worse than ten rivals with open PRs. The
assignee check is the cheaper and more decisive one, so it goes first.

## The Verification Discipline

The fix shipped with a regression test that asserts the rejection in **both**
components, so a future refactor that drops the check in one of them fails
loudly:

```bash
node test-assigned-issues.js   # 11 checks, all must pass
```

A fix with no test is a fix that will be silently undone by the next person
who does not know why the line is there.

## The Generalisation

> **Before you start work on a public task, check the field that records
> ownership.** Assignee, milestone, project board column, "in progress" label,
> a linked branch — every tracker has one. If the task is public and
> claimable, someone else may have claimed it while you were reading the
> body.

This is not only about bounties. It applies to:

- picking an issue to fix in an open-source repo,
- choosing a "good first issue" for a new contributor,
- claiming a `help wanted` ticket in your own team's tracker,
- evaluating a **contribution** task before you invest an evening in it.

See also `prompts/bounty-saturation-detection.md` (competition), 
`prompts/bounty-freeze-detection.md` (closed/frozen), 
`prompts/bounty-pr-finalized-skip.md` (PR already merged).
