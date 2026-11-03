# Capture Before You Reset

**A rule for every `git reset --hard`, `git clean -fd`, branch deletion, or
history rewrite.**

> Found 2026-11-03. A 7-repo backup sweep had to write bundles, worktree and
> index patches, stash lists and untracked-file tars **before** the reset,
> because the reset is what destroys the divergent history. **Last verified:**
> 2026-11-03 — 1.2 MB of capture written to
> `memory/backup-devtools-2026-11-03/`, all 7 repos verified `0/0`
> ahead/behind against `origin/main` afterwards.

## The Rule

> **A reset is a destructive operation. Capture first, reset second, verify
> third. In that order, always.**

## The Numbers That Make It Concrete

Local-only commits on `backup/conflicted-2026-11-03` branches, before the
reset:

| repo | local-only commits |
|---|---|
| `tiny-router` | 16 |
| `tiny-log` | 13 |
| `tiny-validator` | 10 |
| `tiny-cli` | 6 |
| `tiny-config` | 3 |
| `fast-cache` | 2 |

**None of these exist in `origin/main`.** A reset to `origin/main` deletes all
of them, and after the reset they are unreferenced by any branch - a `git gc`
drops them permanently.

## The Capture Set (All Four, Not One)

```bash
# 1. Every commit, including unreferenced ones
git bundle create ../backup/$(basename $PWD).bundle --all

# 2. Uncommitted work in the worktree
git diff > ../backup/$(basename $PWD)-worktree.patch

# 3. Staged work in the index
git diff --cached > ../backup/$(basename $PWD)-index.patch

# 4. Untracked files, which NO diff captures
git ls-files --others --exclude-standard -z \
  | tar --null -T - -czf ../backup/$(basename $PWD)-untracked.tar.gz

# 5. Stash entries, which live outside both diff and bundle
git stash list > ../backup/$(basename $PWD)-stashes.txt
git stash show -p 'stash@{0}' > ../backup/$(basename $PWD)-stash0.patch
```

**The untracked tar is the step people skip.** A diff captures nothing that
was never tracked, and an untracked file is often the only copy of something.

## A Stash Is Not Automatically Unpublished Work

A stash entry can be large and still be worthless. Measured on
`tiny-log stash@{0}`: a **543-line diff (407 insertions / 136 deletions)**
that was **older than the published v0.6.0** - the stashed `tiny_log.py` had **0** `TraceContext` references while the published module has **6**.

**The stash predates the feature that later landed in published form.** It is
not a rescue; it is a draft of history that already exists in better shape.

The discriminator is a diff against the published tree, not the size of the
diff:

```bash
# does the recovered file contain anything the published tree lacks?
grep -c 'TraceContext' ../backup/tiny-log-untracked/tiny_log.py \
  $(git rev-parse --show-toplevel)/tiny_log.py
```

## The Recovered Files Are Not All Duplicates

16 files were extracted from the 7 repos. Measured against the published
trees:

- **genuinely new**: `tiny-validator/_v040.py` contained `OneOf` / `AllOf` /
  `Not` / `Schema` with RFC 9457 Problem Details — **none of those
  combinators appear anywhere in the published `tiny_validator.py`** (grep
  returns 0).
- **genuinely new**: `tiny-cli/tests/{test_progress,test_completion,test_table}.py`
  and the `Completion` class are **missing from the published `tiny_cli.py`
  entirely**.
- **older drafts**: `tiny-log` and `tiny-validator` `CHANGELOG.md` differ from
  published but are older.

**Recovery has to be verified file by file against the published tree, not
assumed useful.** A recovered file nobody reviewed is a liability - see
`prompts/a-stale-clone-is-a-loaded-weapon.md`, where recovered files carried
API claims that were false of the published repos.

## The Verification After The Reset

```bash
for d in fast-cache snapdb tiny-cli tiny-config tiny-log tiny-router tiny-validator; do
  printf '%-16s %s\n' "$d" "$(git -C repos/$d rev-list --left-right --count @{u}..HEAD)"
done
# every row must read "0<tab>0"
```

## The Generalisation

**Any destructive operation that discards history needs a capture immediately
before it.** The same rule covers `rm -rf` on a directory, `docker volume rm`,
and a database DROP. The capture is cheap; the loss is not recoverable.

See also `prompts/a-stale-clone-is-a-loaded-weapon.md` (the clone that could
push to the real remote) and `prompts/safe-file-write-append.md` (the writer
that silently replaced a file instead of appending).
