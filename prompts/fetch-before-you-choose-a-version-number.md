# Fetch before you choose a version number — the remote may already own it

**Last verified: 2026-11-26** — triggered by two rejected pushes in one session
(`tiny-validator` and `snapdb`, both version bumps). The fix below is the
procedure that worked, re-run once per repo.

## The failure

```
edit pyproject.toml -> 0.7.4
git commit -m "chore(release): 0.7.4"
git push
# ! [rejected]  main -> main (fetch first)
# remote main already had 0.7.4, merged two days earlier from another session
git rebase
# CONFLICT (content): CHANGELOG.md  -- both sides added a section, same heading
```

The local clone's top CHANGELOG entry describes **local head**, not what is
published. A repo can be several commits behind and nothing looks wrong: the
tests pass, the version guard passes, the changelog reads correctly. **A local
version number is a guess until you fetch.**

## Procedure

```bash
git fetch origin
git log --oneline HEAD..origin/main          # what you are missing
git show origin/main:CHANGELOG.md | head -20 # the REAL newest section
# choose the next number from that, not from your local file
```

Then bump, and **count the version surfaces from the repo** — grep, do not
remember:

```bash
grep -rn "0\.18\.5" --include="*.py" --include="*.toml" \
      --include="*.json" --include="*.md" . | grep -v CHANGELOG
```

`snapdb` carries its version in **three** places (`snapdb/__init__.py`,
`pyproject.toml`, `package.json`); the first bump in this session edited two and
`test_version_consistency` failed on the third. That test earned its keep — the
lesson is that *"bump the version" is a multi-file edit whose file list should be
read from the repo, not recalled.*

## After a rejected push

1. `git fetch`, read `origin/main`'s newest CHANGELOG heading.
2. Rebase. On a CHANGELOG conflict keep **the remote entry as published** at the
   top and renumber **yours** above it.
3. Re-apply every version surface (grep again — the rebase may have restored an
   older number in a file you already edited).
4. Re-run the suite and the version guard **after** the rebase, not before.
5. Push. If it is rejected a second time, the remote moved again; repeat rather
   than force.

## What not to do

- Do not `git push --force` to "win" the number. Someone else's published 0.7.4
  has consumers; renumbering yours is one edit.
- Do not resolve the CHANGELOG conflict by deleting the remote section. The
  published entry is the one users already installed.
- Do not trust `git status` to show this. Nothing is dirty; the local branch is
  simply behind, and every check passes on the stale tree.

Related: `rebase-before-writing-the-changelog-section.md`,
`a-version-guard-only-covers-the-files-it-reads.md`.
