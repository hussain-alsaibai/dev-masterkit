# A Stale Clone Is A Loaded Weapon

**A rule for any backup clone, mirror, or working copy that shares a remote
with a repository you also push from.**

> Found 2026-10-27. Three backup clones of `dev-masterkit` had `origin`
> pointing at the **real** GitHub repository and were 67-72 commits behind.
> There was no branch protection and no ruleset, so a force push from any of
> them **would have succeeded**. **Last verified:** 2026-10-27 — the dry run
> below was executed against all three clones before anything was deleted.

## The Rule

> **A backup clone of a repo you also push from is a loaded weapon. Separate
> it in one of two ways: give the backup a different remote, or make it unable
> to push.**

## The Numbers

| clone | behind | files a force push would delete |
|---|---|---|
| `dev-masterkit-clone` | 67 | 210 |
| `dev-masterkit-check` | 72 | 222 |
| `dev-masterkit-sync` | 71 | 222 |

Those deletions included `.github/workflows/ci.yml` — the CI added the day
before — and every `daily-updates/` file after 2026-10-05.

**A force push that reports *forced update* is fine. A force push that
reports deletions is a catastrophe with a green checkmark.**

## The Dry Run — Run It Before Every Force Push

```bash
# 1. How far behind is this clone?
git rev-list --left-right --count origin/main...HEAD
# behind  ahead
#      72      0

# 2. WHAT WOULD BE DELETED. This is the command that matters.
git push --dry-run --force origin main
git diff --name-status origin/main HEAD | grep -c '^D'
# 222
```

A non-zero deletion count is a stop sign, not a confirmation.

## The Fix That Was Applied

The backup clones were pointed at a path that does not exist:

```bash
git remote set-url origin \
  file:///home/node/.openclaw/workspace/.disabled-remote/dev-masterkit.git
```

Any push from them now fails with *"does not appear to be a git repository"*
and nothing else changes. The real clone kept the real URL.

**Verify the fix by trying to push**, not by reading the config:

```bash
git -C dev-masterkit-clone push --dry-run origin main
# fatal: 'origin' does not appear to be a git repository
```

## Before Deleting A Clone At All

> **Diff it against the real remote, file by file. A stale clone often holds
> the only copy of something that was never published.**

```bash
comm -23 <(git -C clone ls-tree -r --name-only HEAD | sort) \
         <(git ls-tree -r --name-only origin/main | sort)
```

In this instance that command showed exactly two files that existed nowhere
else. They had been sitting unpublished for 8 days.

**And then review them.** A recovered file that nobody reviewed is a
liability, not a rescue. Both files were full of claims that were false of
the published repositories:

- the guide's sizing table was wrong in two of three rows (off by two orders
  of magnitude in one),
- the report described three features (`TraceContext`, `FileWatcher`,
  `If`/`Unless`) that existed only in abandoned local copies and were never
  pushed.

Every API claim was re-verified against the published `main` branch before
publishing, and the false ones were **rewritten rather than copied**.

## The Generalisation

This applies to any duplicate working copy: a CI runner checkout, a backup,
a worktree, a scratch clone. **Ask of each one: can it push, and where?**

The safe state for a backup is a remote that cannot be reached. The second
best state is a remote that is not the thing you are protecting.

See also `prompts/assigned-issue-is-a-taken-issue.md` (the claim check) and
`prompts/external-bounty-clean-branch.md` (clean-branch hygiene for work that
will be pushed).
