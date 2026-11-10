---
name: external-pr-rebase-and-maintenance
description: "Resolve a CONFLICTING external PR against a moved upstream - classify the upstream commits, prove failures are pre-existing with a worktree baseline, force-push pinned to the previous SHA, re-arm the review gates, and route out-of-scope review findings to an upstream issue. Use when a shared PR goes CONFLICTING/DIRTY, when a review bot raises a finding of uncertain scope, or before force-pushing to a branch another session may also be working on."
---

# external-pr-rebase-and-maintenance — keep a shared PR mergeable without losing anyone's work

**Last verified:** 2026-11-10

A procedure for the maintenance half of an external contribution: a PR that is
open, reviewed, and has gone `CONFLICTING` because upstream moved. The work was
already done; this is the part that decides whether it lands.

## When to use

- `gh pr view <n> --json mergeable` returns `CONFLICTING` / `DIRTY`
- Upstream landed commits that touch the same files
- A review bot raised a finding that may or may not be in scope

## Step 0 — is anyone else already doing this?

```bash
gh pr view <n> --json headRefOid,mergeable,baseRefName,state
```

Compare `headRefOid` to the SHA your plan expects to replace. If it is not
that SHA, someone else is working here. See
`prompts/check-whether-the-fix-already-landed.md`.

## Step 1 — read what upstream actually changed

```bash
git fetch origin
git log --oneline HEAD..origin/main -- <the files you touched>
```

Classify each upstream commit before resolving anything:

1. **The file you edited was deleted.** Accept the deletion, then port your
   change into whatever replaced it — a workflow, a module, a test file. Do
   not resurrect the deleted file.
2. **The function you call was renamed.** Port the call site **and** the test
   assertion. A test that asserts `assert_called_once_with()` breaks when the
   default argument becomes an exported path.
3. **Additive edits on the same file.** Both sides keep their tests. This is
   the common case and the one people over-resolve.

## Step 2 — resolve as two changes, not one merge result

For a purely additive conflict, keep both blocks and verify by name:

```bash
grep -c '^def test_' tests/<file>.py     # expect upstream + yours
git diff --stat origin/main...HEAD
```

## Step 3 — prove the failures are pre-existing with a worktree

Never `git stash` to get a baseline. Use a separate working tree:

```bash
git worktree add /tmp/<repo>-main origin/main
cd /tmp/<repo>-main && pytest -q > /tmp/base.txt 2>&1
```

Then diff the **sorted failure lists**, not the counts:

```bash
grep -E '^(FAILED|ERROR)' /tmp/base.txt   | sort > /tmp/base.sh
grep -E '^(FAILED|ERROR)' /tmp/branch.txt | sort > /tmp/branch.sh
comm -3 /tmp/base.sh /tmp/branch.sh
```

Empty `comm` output = zero regressions **and** zero newly-fixed. The second
half matters: a rebase that accidentally fixes something is also a rebase you
did not understand.

Point `--basetemp` off the tmpfs first — see
`prompts/a-rerun-is-not-a-rerun-if-the-tempdir-was-full.md`.

## Step 4 — push without overwriting anyone

```bash
git push --force-with-lease=<branch>:<exact-old-sha> origin <branch>
```

Pinned to the SHA you rebased from. Fails if anyone moved the branch, which is
the entire point. Never a bare `--force`.

## Step 5 — re-arm the review gates

A new commit on a reviewed PR usually reopens the gates:

- PR converts back to **draft** — nothing is being reviewed until you un-draft
- "Author reviewed the PR" style bots reset to `pending`
- CodeRabbit and friends only re-review on new activity

Sequence: post the acknowledgment for the new SHA -> wait for it to go
`success` -> `gh pr ready` -> check `gh pr checks <n>` once.

## Step 6 — classify the remaining reds honestly

| Red | Owner |
|---|---|
| `license/cla` pending | **human** — a legal signature, never automated |
| `action_required` on a fork PR's workflow | **human** — maintainer approval to run |
| AI-policy / provenance question | **human** — an unattended-agent PR may be closed on policy |
| a duplicate PR by another contributor | **human** decision on comment vs withdraw |
| your own lint/test failure | **you** |

Naming a red as a human action is a completed piece of work. Retrying around a
CLA signature is not.

## Step 7 — out-of-scope findings go upstream, not into the PR

If a review finding is real but fixing it means changing the guest process
model, the public API, or behaviour for every caller — file it as an issue with
your full analysis, cross-link, and reply in the PR explaining the scope line.
Quote the design doc or issue that bounds the PR. This preserves the finding
without turning a reviewed PR into an unreviewable refactor.

## Anti-patterns seen in practice

- **Porting the fix but not the test assertion** — the test passes locally
  against the old signature and fails only in CI.
- **Keeping a deleted file alive "because it has our change in it"** — the
  workflow no longer runs; the change is decorative.
- **`--force` after a rebase** — clobbers a concurrent push with no error.
- **Stash-based baselines** — one interrupted command loses the work being
  measured.
- **Fixing an out-of-scope finding in the PR** — swaps a mergeable PR for a
  design debate.

## Verification log

| Date | PR | Situation | Outcome |
|---|---|---|---|
| 2026-11-10 | `boxlite#2460` | timeout forwarding + native-boundary tests | **merged** as `fe6c4d1b` |
| 2026-11-10 | `amd/gaia#6589` | upstream deleted our workflow, renamed a loader | rebased, `MERGEABLE`, 2376 passed |
| 2026-11-10 | `AgenticResourceRegistry#2027` | additive test conflict, AI-policy repo | rebased, `MERGEABLE`, CLA pending (human) |
| 2026-11-10 | `boxlite#2513` | out-of-scope finding from review | filed upstream, maintainer acknowledged |
