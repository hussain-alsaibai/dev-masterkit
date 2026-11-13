# Rebase before writing the changelog section

**Last verified:** 2026-11-13 (12:00 EST) — `tiny-validator` push rejected:
remote `main` **4 commits ahead**, with **0.7.0 published the day before** by
another session; the branch was based on 0.6.0.

## The rule

> **`git log HEAD..origin/main` before writing the changelog section.**

I wrote a `0.6.1` entry for a repo at `0.7.1`. The repo's own version
consistency test rejected it — which is how the divergence surfaced, not how it
was caught earlier.

## The second discovery

The 0.7.1 commit upstream was already a fix for **the same class of bug** I was
fixing (`required` inferred from `field.required` instead of
`required and default is ...`). Two sessions found the same defect the same day.

**Rebase by re-applying your edits to `origin/main`'s file, then credit the
upstream fix** rather than duplicating it under a new number. A second fix for a
fixed bug is a duplicated changelog entry and a merge conflict for the next
session.

## Sequence

```sh
git fetch origin
git log --oneline HEAD..origin/main          # what shipped without you
git show origin/main:<file>                   # read the actual state
# re-apply your edit to origin/main's version, new version number from THERE
```

## Why "push rejected" is good news

A rejection for being behind means someone else published. The alternative — a
push that succeeds because nobody else was pushing — is indistinguishable from
success and much worse.
