# A Gitlink Without A .gitmodules Entry Is Broken For Everyone

**A rule for any repository that carries mode `160000` entries — a gitlink
that no clone can check out.**

> Found 2026-11-03. `bounty-hunting` carried **2 mode-160000 entries** with no
> `.gitmodules` file at all. **Last verified:** 2026-11-03 — reproduced with
> `git submodule status` on a clean checkout:
> `fatal: no submodule mapping found in .gitmodules for path
> 'bounty-hunting/modelscan'`.

## The Rule

> **A gitlink is a promise about a URL. Without the `.gitmodules` entry that
> names the URL, the promise is unresolvable and every clone is broken.**

## The Evidence

```bash
$ git ls-files -s | awk '$1==160000'
160000 abc4b1510315ba1ba162e3ae002e5d394db32200 0\tmodelscan
160000 806426784adb43631e9a1102d4621126bb589347 0\tsafetensors

$ ls .gitmodules
ls: cannot access '.gitmodules': No such file or directory

$ git submodule status
fatal: no submodule mapping found in .gitmodules for path 'bounty-hunting/modelscan'
```

Mode `160000` is git's way of recording *"this path is a submodule, and here
is the commit it points at"*. The **URL** lives in `.gitmodules`, not in the
tree entry. With the tree entry present and the file absent, the clone
succeeds, the path appears as an empty directory, and `git submodule status`
aborts.

## Why It Is Silent Locally And Loud Everywhere Else

The directories existed on disk in the working copy, so nothing looked wrong.
The **failure lands on the next person**:

| step | result |
|---|---|
| `git clone` | **succeeds** — the gitlink is just a tree entry |
| `git checkout` | succeeds, path is an empty dir |
| `git submodule update --init` | **fatal** — no mapping found |
| any CI that runs `submodule update` | **red, with a confusing error** |

The commit SHA in the tree entry (`abc4b151...`) is *not* usable without the
URL. **The tree records the destination; `.gitmodules` records the route.**

## The Procedure

1. **Find every gitlink in the tree**:

```bash
git ls-files -s | awk '$1==160000 {print $4}'
```

2. **Check that every one of those paths has a `.gitmodules` mapping**:

```bash
for p in $(git ls-files -s | awk '$1==160000 {print $4}'); do
  git config -f .gitmodules --get-regexp "submodule\\..*\\.path" | grep -qx "$p" \
    || echo "MISSING MAPPING: $p"
done
```

3. **Two legitimate repairs**, and they are not interchangeable:

| situation | repair |
|---|---|
| the submodule is a real dependency you want | add the `.gitmodules` entry with the correct URL, and keep the gitlink |
| the directory is a **vendored copy** you want to keep | `git rm --cached <path>` and commit the files as ordinary blobs — **remove the gitlink** |

4. **Never `git add` a directory that is itself a git repo** without deciding
   which of the two you want. `git add` on a nested repo creates the
   gitlink automatically, and it is easy to do by accident.

## The Recovery That Was Applied

The two broken gitlinks (`modelscan`, `safetensors`) were removed from the
index and the underlying content preserved as ordinary files, together with
the `FINDINGS.md` and all three proof-of-concept files that lived beside
them. **The commits were removed; the work was kept.**

**Removing a broken reference is not the same as removing the work.** Verify
what the gitlink was pointing at before you drop the SHA — the SHA is the
only record of which upstream commit you meant.

## The Generalisation

This is a git-level instance of a broader rule: **a reference that resolves
through a side file is a reference that can be broken without touching the
reference itself.** Same shape as a CI workflow that references a script path
nobody moved, or a README that points at a file renamed six months ago.

See also `prompts/ci-target-must-match-repo-layout.md` (a workflow that
points at a path that is not there).
