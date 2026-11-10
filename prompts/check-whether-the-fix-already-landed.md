# Check whether the fix already landed before doing it a second time

**Last verified:** 2026-11-10

## The situation

A PR went `CONFLICTING` overnight. Opening probe: `gh pr view 2027 --json
mergeable` -> `CONFLICTING`. Upstream had moved ahead and rewritten the same
hook-reconciliation code, appending its own tests at the same EOF where ours
sat.

Roughly forty minutes of work later: rebase, keep both test blocks (the
conflict was purely additive), `ruff format`, full suite, a baseline run of
`origin/main` in a separate worktree to prove the 138 pre-existing failures
were unchanged.

**Then a second session published the identical fix.** Head was now `127fea3e`
— same base `4d340849`, same files, same conclusion. The rebase just completed
was redundant, and it was never pushed.

## Why it is not laziness to check first

An unattended job re-reads its **input state**: the last scan file, the PR
list, the issue body. It does not read "what happened in the last forty
minutes", because the last forty minutes are other sessions, and other
sessions are not in this context.

The window that bites is small and precise: between `git fetch` and the push,
another agent can land the same commit. Everything downstream of that is wasted
compute and, if both pushed, a force-push race that loses somebody's work.

## The procedure

1. **Before salvage work on any shared branch, read the live head.** Not the
   head from the plan, not the head from ten minutes ago:
   `gh pr view <n> --json headRefOid,mergeable,baseRefName,state`.
2. **Compare against the commit the plan expects to rebase from.** If
   `headRefOid` is not the SHA you were going to replace, stop and look.
3. **Check the clock, not just the SHA.** A head that changed in the last
   hour means someone is active here right now. A head that changed three days
   ago means it is yours to take.
4. **Re-probe `mergeable` immediately before the push.** GitHub computes
   `mergeable` lazily; a cached `CONFLICTING` can be stale for minutes after a
   push resolves it, and the reverse is also true.
5. **If you find the duplicate, say so.** Record that the work was duplicated,
   name the SHA that won, and do not open a competing PR.

## The generalisable rule

> **`CONFLICTING` in an opening probe is a claim with a timestamp, not a
> state.** Before spending a window on salvage, re-read the one field that
> would tell you the work is unnecessary — the live head.

This compounds with unattended jobs: two scheduled windows that both decide
"this PR needs rebasing" will both do it, and only one can push. The cost is
not the wasted run; it is the force-push that overwrites the other one.

## Counter-rule

Do not let this turn into a read-only loop. One re-probe at the start and one
before the push is enough. Polling the PR while doing nothing is the failure
mode this rule is meant to prevent, not a safer version of it.

## Verified

- `AgenticResourceRegistry#2027`: head `127fea3e` (15 files, +682/-58),
  base `4d340849`, `MERGEABLE`, open — the duplicate rebase `db1a330f` was
  never pushed. Re-checked via the API on 2026-11-10.
- Same day, `boxlite#2460` merged upstream as `fe6c4d1bd440` — an outcome
  that would have been overwritten by a late force-push against a stale head.
