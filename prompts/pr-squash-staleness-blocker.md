# PR Squash-Staleness Blocker — When `allow_update_branch=false` Kills PR Merges

**Created:** 2026-08-25
**Last verified:** 2026-08-25
**Author:** OpenClaw / hussain-alsaibai
**Source:** snapdb PR #32 blocked after sibling PR #30 squash-merged into main

---

## The Problem

You have two open PRs against the same repo:

- **PR #30** (`fix(test-fixture-name)`) — green CI, MERGEABLE, trivial
- **PR #32** (`feat: DocumentStore.search()`) — green CI, MERGEABLE, ready

You merge #30 (squash) into `main`. Now #32's head branch is **behind `main`** — but `#32` shows MERGEABLE, no conflicts listed.

When you try to merge #32:
- `gh pr merge --squash --admin` → "7 of 7 status checks expected" (unhelpful)
- `gh pr update-branch` → silent failure (exit 0, no-op)
- Web UI → "This branch is out-of-date with base branch but is mergeable"

The PR is mergeable but cannot be merged. You are stuck.

---

## Root Cause

The repo has **`allow_update_branch=false`** (or equivalent, via Branch Protection Rule or repo defaults). This means GitHub will NOT automatically update a PR's head branch to rebase against new commits on the base branch.

After a squash merge of a **sibling** PR (#30), the base branch (`main`) now has a new commit. PR #32's head is now out-of-date. Normally GitHub would show "Update branch" and either:
1. **auto-merge** if `auto-delete-head-branch=true` + `require branches up to date before merge = false`
2. **offer "Update branch" button** for the user to click

But with `allow_update_branch=false`, neither option works. The PR stays "out-of-date but mergeable" forever.

### Why `gh pr update-branch` silently fails

`gh pr update-branch` calls `PUT /repos/{owner}/{repo}/pulls/{pull_number}/update-branch`. This endpoint is **disabled** when `allow_update_branch=false`. The API returns 200 (success), but the update is a no-op. `gh` shows no error — it just doesn't work.

### Why `gh pr merge --squash --admin` fails

The mergeability check still runs, and GitHub blocks the merge because the head branch is behind. The `--admin` flag bypasses some checks but not the staleness gate.

---

## The Fix

### Option A — Enable `allow_update_branch` (preferred, one-line)

```bash
gh repo edit <owner>/<repo> --enable-update-branch
```

This lets GitHub auto-update PR head branches before merging. One command, no downtime.

**Why this is safe:** It doesn't weaken branch protection — it only allows GitHub to rebase/fast-forward the PR head *in the background* before merge. The base branch (`main`) is never modified. Review requirements, status checks, and required approvals still apply.

**Verify:**
```bash
gh repo view <owner>/<repo> --json updateBranchOnMerge
# Should show: true
```

### Option B — Rebase manually and push

```bash
git fetch upstream
git checkout pr/32-feat-document-store-search
git rebase upstream/main
git push --force-with-lease
# Now the PR head is up-to-date, merge works normally
```

**Caution:** `git push --force-with-lease` rewrites the branch history. Use `--force-with-lease` (not `--force`) so it fails if someone else pushed to the branch.

### Option C — Web UI merge

Go to the PR page → "Merge" button → GitHub will either merge directly (if auto-update works) or show "Update branch" → click it → merge.

This is the fallback when neither CLI nor API can update the branch.

---

## Prevention

Before opening multiple PRs against the same repo, check the branch protection settings:

```bash
gh api repos/<owner>/<repo> --jq '.allow_update_branch'
# false = at risk; true = safe

# Also check branch protection rules
gh api repos/<owner>/<repo}/branches/main/protection --jq '.required_status_checks.blocks_renovation'
```

**Rule:** On repos you control (`hussain-alsaibai/repos`, `context-bridge`, etc.), always enable `allow_update_branch=true`. It costs nothing and prevents the stuck-PR scenario entirely.

For external repos (bounty targets): accept the risk, and **merge PRs in dependency order** — if PR B depends on changes in PR A, merge A first, then B will naturally be up-to-date.

---

## When Merging Multiple Sibling PRs

When you have 2+ PRs against the same base and want to merge them both:

1. **Merge in dependency order** — if PRs touch the same files, merge the "lower" one first
2. **Check `allow_update_branch`** before starting — if false, rebase each sibling PR before merging the next
3. **Watch for the squash-merge race:** after merging #30, immediately rebase #32 before doing anything else

```
PR #30 merge → main has new commit → PR #32 head is now behind
                        ↓
              [REBASE PR #32 NOW, before anything else]
```

---

## Decision Rules

| Signal | Action |
|--------|--------|
| `allow_update_branch=false` on owned repo | Flip it to `true` — one-line fix |
| `allow_update_branch=false` on external repo | Accept risk; plan merge order + manual rebase |
| PR "out-of-date but mergeable" after sibling merge | Rebase immediately: `git rebase upstream/main` |
| `gh pr update-branch` silently succeeds but PR still won't merge | API disabled; use manual rebase or web UI |
| Multiple PRs open on same repo | Merge in dependency order; rebase any that fall behind |

---

## Related Prompts

- `already-merged-skip.md` — skip bounties already resolved upstream
- `bounty-pat-fine-grained-fixes.md` — PAT scope limitations for cross-repo PRs
- `external-bounty-clean-branch.md` — clean branch preparation workflow
