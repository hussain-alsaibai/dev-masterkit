---
name: no-checks-reported-is-not-checks-failed
description: Use when a pull request looks untested — distinguish "no CI ran" from "CI failed" from "CI is queued waiting for a maintainer to approve a fork workflow".
---

# `no checks reported` is not `checks failed`

## The prompt

> You are deciding whether a pull request has been tested. Before you conclude
> anything from the check list:
>
> 1. `gh pr checks <n>` lists **check-runs**. A workflow gated by GitHub is
>    queued with **no check-run**, so it prints `no checks reported` and looks
>    identical to a PR with no workflow at all.
> 2. Ask the run list instead:
>    `gh run list --branch <branch> --limit 10 --json status,conclusion,headSha,event`.
> 3. If runs exist with `conclusion: action_required`, the workflow is
>    **waiting for a human to approve it**. That is not a failing test, not a
>    missing trigger, and not something a force-push will fix.
> 4. Confirm `headSha` matches your current commit. A rebase or force-push
>    restarts the approval gate, so the runs you are looking at may be stale.
>
> Three states, three different actions. Reading them as one state wastes a
> debugging cycle every time.

## Why

`revertinc/revert#706` and `zzet/gortex#1418` both looked untested on
2026-11-14:

```
$ gh pr checks 1418 --repo zzet/gortex
no checks reported on the 'doctor-legacy-state' branch
```

The runs existed:

```
conclusion: action_required
headSha:    4a31f7a3e663      # my exact commit
event:      pull_request
created:    2026-11-14T08:16:59Z
```

`action_required` is GitHub's **approval gate for workflows on pull requests
from forks**. The maintainer has to click approve before a single job runs.
The PR is not failing and the trigger is not broken — it is waiting.

## The three states, and what each one means

| what you see | command that shows it | what it means | what to do |
|---|---|---|---|
| `no checks reported` | `gh pr checks` | a gated run has no check-run | go to the run list |
| `action_required` | `gh run list --branch` | queued, awaiting maintainer approval | nothing — say so in the PR |
| `failure` | `gh pr checks` / `gh run view` | a job ran and did not pass | read the log |

Only the third is a test result. The first two are the absence of one, and an
unattended work loop that treats them as failure will keep re-pushing commits
that were never the problem.

## The related trap: a green check that tests nothing

The same review turned up the mirror image. `revertinc/revert` has no code CI
on pull requests at all — `.github/workflows/` holds `check-pr-title.yml`, a
docs preview, and deploy-on-main jobs. A green check on a PR there means **the
title was well-formed**.

Rule: before treating a check as evidence about code, read what the workflow
actually runs. `yaml`-level presence of a workflow is not coverage of the
diff.

## The local fallback when CI cannot run

When the gate is external and the repo has no code CI, the local gate is the
only one available — and on `revert` the typecheck had a **509-error
baseline** on `main`. The absolute number is meaningless; the delta is the
signal:

```bash
# on origin/main, and on your branch, in the same environment
tsc --noEmit 2>&1 | sed -E 's/\(([0-9]+),[0-9]+\)/(\1)/' | sort > /tmp/base.txt
comm -13 /tmp/base.txt /tmp/branch.txt
```

Normalize away the line **and column** before comparing — your edits move
them, and a column difference reads as a new error.

That diff named a real defect in the patch: `'integrationId' is declared but
its value is never read` at `workday.ts(18,9)` — the parameter was
destructured and then `TP_ID.workday` hardcoded at all three call sites, while
the sibling handlers used the parameter.

See also `prompts/ci-that-is-not-auto-triggered-is-ci-that-ran-once.md` and
`prompts/a-ci-workflow-on-a-branch-that-does-not-exist-is-not-ci.md`.

Last verified: 2026-11-14 — `gh pr checks`, `gh run list --branch` and the
typecheck delta reproduced on `zzet/gortex#1418` and `revertinc/revert#706`.
