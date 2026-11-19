---
name: disk-prune-that-actually-frees
description: "Diagnose and repair a disk-prune job that reports success but frees nothing, find the real space consumers, set a threshold that survives the workload's growth between prunes, and refuse to delete the paths that are live or irreplaceable. Use when a container or host is near full, when a prune runs on schedule and df does not move, or before widening a prune target list."
---

# disk-prune-that-actually-frees — measure the prune, then set the line below it

**Last verified:** 2026-11-19 (this host: `91% -> prune -> 89% -> one go build -> 91%`;
`go clean -modcache` on a stale 1.2 G cache; `rm -rf` refused on read-only module files)

A prune job that runs and frees nothing is worse than no prune: it produces a
green job, a log line saying "pruned", and a disk that keeps climbing.

## Step 1 — read the before/after numbers, not the exit code

```
disk-check: 91% -> 91%
```

That line is a failure report. A prune whose two numbers match did not prune
**the thing that is big**. Record `df -h /` before and after in the same run;
anything else is a claim.

## Step 2 — compare the target against the filesystem, not the config

The 2026-11-19 case: the script deleted `/home/node/go/pkg/mod/cache`, which was
**empty**. The real stale cache was `/home/node/go-mod` (**1.2 G**, last written
2026-07-08). `go env GOMODCACHE` pointed at a third, nearly empty path.

```bash
go env GOMODCACHE GOPATH GOCACHE
du -sh /home/node/go-mod /home/node/go/pkg/mod /home/node/.cache/go-build 2>/dev/null
```

The tell for a stale module cache: Go's **escaped-path layout** (`!azure`,
`!proton!mail`), no `cache/download/` half, and an mtime months old.

## Step 3 — `rm -rf` cannot remove a module cache

```
rm: cannot remove '/home/node/go-mod/modernc.org/libc@v1.73.4/include/...': Permission denied
```

Go marks those files read-only. Use Go's own removal path:

```bash
GOMODCACHE=/home/node/go-mod go clean -modcache   # -> 1.2G freed
go clean -cache                                    # build cache
```

Same class: `npm` content caches, `.cache/ms-playwright` after a browser
version bump, `.git` object packs after a history rewrite — each has a tool that
knows its own layout. Prefer it to `rm` for anything a package manager owns.

## Step 4 — set the threshold below the line, by the size of the growth

Measure what the workload adds between prunes. One `go build` here adds **2.1 G**
(module cache 2.0 G + build cache 322 M):

| prune fires at | after a 2.1 G build | `df` reports |
|---|---|---|
| 88% | 90.19% raw | **91%** — still alerting |
| 86% | 88.19% raw | 89% — clear |
| 84% | 86.19% raw | 87% — clear |

A prune at the alert threshold oscillates around it forever. Threshold moved to
**85%**.

**Rule: the threshold is not the alert number. It is the alert number minus the
largest thing that grows between prunes.** Measure the growth once; do not reason
about it.

## Step 5 — classify every remaining large directory before touching it

On this host after freeing the stale cache: **89%, 11 G free**. The four largest
remaining paths were all untouchable, and a prune target list that names them is
a data-loss bug with a scheduled delivery:

| path | size | why it stays |
|---|---|---|
| `openclaw-agent.sqlite` | 1.3 G | the **live** database — 5 free pages of 319,097, so there is no bloat to reclaim |
| `tmp/plugin-captures/...` | 853 M | held open by a running process — `ls -l /proc/*/fd` confirms |
| `memory-backup-2026-10-24.tar.gz` | 637 M | the **only** copy of the unpushed git bundles; the directory it came from is gone |
| `github/` | 2.6 G | clones with unpushed commits |

Checks before deleting anything large:

```bash
df -h /                                  # current headroom
du -sh /path                             # size
ls -l /proc/*/fd 2>/dev/null | grep -F /path   # is a process holding it?
sqlite3 db "PRAGMA freelist_count; PRAGMA page_count;"   # live rows vs bloat
git -C clone status -sb | head -1         # unpushed commits?
```

## Step 6 — a backup that is the only copy is not a backup

The 637 M tarball predated a cleanup that removed the directory it held. Before
deleting any archive, check that the thing it protects still exists somewhere
else. If not, the archive **is** the work, and the prune must name it as a
never-touch target explicitly rather than skip it by accident.

## Reference implementation

`scripts/prune-disk.sh` (copied verbatim from the live health-monitor skill on 2026-11-19) encodes steps 1–6: `df` numbers printed
before and after, both module caches cleaned via `go clean -modcache`, the
tarball and the live database named as never-touch, 85% threshold.

## Anti-patterns

- Moving the threshold **up** when the disk fills (it makes the alert quieter and
  the disk fuller).
- Deleting a path because it is large. Size is not permission.
- `find / -size +500M -delete` on a live host: it will eventually find a socket,
  a database, or a backup.
- Trusting a `VACUUM` to shrink a database that is 99.998% live pages.
- Adding a cache to the prune list without a package-manager command to clean it.
