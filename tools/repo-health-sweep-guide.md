# repo-health-sweep — fleet CI status must read the newest run on the default branch

**Last verified:** 2026-11-07

A single-file node script (`repo_health_check.js`) that walks every repository
under one owner and assigns GREEN / YELLOW / RED from CI runs, open issues,
open PRs and star deltas. It is small enough that its failure modes are all in
the *selection logic* rather than the API calls — which is exactly where it
went wrong twice.

## The two bugs, in order

**2026-11-06 — the window rule.** CI status was computed by counting failures
across the last five runs. A repository with 41 newer green runs on `main` and
one old red run was painted RED. Measured: **42 of 173** repos red while 41 of
those had a newer green run on the default branch.

The fix introduced `latestBad`: the newest completed run **on the repo's
default branch**, resolved from `defaultBranchRef.name`, not from run order
alone.

**2026-11-07 — the fix that missed its own assignment.** The line that actually
set RED was still

```js
if (latestBad || failingRecent.length > 0) { status = 'RED'; }
```

and `failingRecent` is *any bad run since the previous check* — the exact window
rule the previous day's entry bans. The 2026-11-06 commit corrected `latestBad`
and the summary line, so the fix read as applied and the bug survived a day.

Live symptom: `tiny-dist-audit`, first sweep after creation, reported
**RED / "CI failing (main, 2026-11-06)"** — while `main` was green.

| run | time (UTC) | conclusion |
|---|---|---|
| `0420616` | 13:05:29 | failure |
| `5b9f4ff` | 13:07:00 | failure |
| `0b4c8fe` | 13:08:30 | **success** (fix: invoke the module, not a console script) |

All three were pushes to `main` inside three minutes. The last one repaired what
the first two hit; the "any failure in the window" rule never noticed.

## The corrected rule

- RED is set by `latestBad` **only**.
- `failingRecent` is still computed, but reported as `recoveredCi` — history,
  not status. A repo that failed and then went green is a **recovery**, which is
  information worth surfacing and wrong to call a failure.
- **Staleness is not failure.** 46 repos had a successful-but-stale newest run
  (9–12 days; `tiny-rbac` 101 days). That is a cadence signal and must never be
  folded into the RED predicate.

## Measured after the fix

`node repo_health_check.js`, full owner sweep:

| field | value |
|---|---|
| `totalRepos` | **173** (171 public, 2 private, 13 forks) |
| `runtimeRed` / `failingCi` | **0 / 0** |
| `activeWorkflowRepos` | **141** |
| never-run non-forks | **19** |
| open issues / PRs | 0 / 0 |
| stars | 6 (0 delta) |
| `recoveredCi` | 0 at the time of the re-run |

## Rules this adds

> **When you change a status rule, grep the whole file for every use of the old
> predicate.** `grep -n "failingRecent"` would have caught the surviving line in
> two seconds. Correcting the value and the summary is not correcting the rule.

> **A predicate name that says "recent" is a bug waiting for its second reader.**
> Name it for the window it measures, and keep the window out of anything that
> assigns a status.

> **Recovery and failure are different events.** If the newest state on the
> default branch is green, the repo is green; the earlier red belongs in a
> history field with its superseding run attached.

> **A first sweep of a brand-new repo is the best detector of window bugs.**
> New repos fail and get fixed within minutes, so any "recent failures" rule
> will fire on them while their actual state is green.

## Denomination caveat

The counts above are the owner's fleet as enumerated by `gh repo list`, one
page at a time (a single `?per_page=100` read silently truncates). They are a
census of *this* fleet, never a claim about the wider ecosystem.
