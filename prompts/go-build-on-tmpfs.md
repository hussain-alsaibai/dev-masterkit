# Go build on a small `/tmp` (tmpfs) — `no space left on device` workaround

## What this solves

On hardened container hosts (including OpenClaw's Debian 12 sandbox),
`/tmp` is often a 256 MB tmpfs. `go build` and `go test` write a large
intermediate file called `importcfg` to `$TMPDIR` during compilation, and
that write silently fails partway through with `no space left on device`
even when `df -h /tmp` shows the tmpfs 80% empty at the start.

The error message is misleading: it's not actually out of *space*, it's
that the per-file write exceeds the tmpfs's `size=` limit, or the
fragmented tmpfs can't satisfy the write atomically.

## Symptoms

- `go build ./...` fails mid-compilation with `importcfg: no space left on device`
- `df -h /tmp` shows plenty free
- `du -sh /tmp/*` shows only a few MB in use
- Re-running the build sometimes succeeds and sometimes doesn't
  (because of fragmentation / race with concurrent builds)

## Fix

Point `TMPDIR` at a real-disk directory with at least 1 GB free:

```sh
mkdir -p ~/go-build-tmp
export TMPDIR=$HOME/go-build-tmp
export GOFLAGS="-tmpdir=$HOME/go-build-tmp"   # belt-and-braces
go build ./...
```

The `$TMPDIR` env var is what the Go toolchain actually honors for
`importcfg` and friends; `GOFLAGS=-tmpdir` is the supported flag form.

For large projects (Gitea, Kubernetes, etc.) also consider:

```sh
export GOCACHE=$HOME/go-cache       # module download cache
export GOMODCACHE=$HOME/go-modcache # module storage
```

These can each be multiple GB on a big build and are independent of the
tmpfs size limit.

## When you don't have a real disk either

If the entire workspace is on tmpfs (rare), use a `tmpfs` with a higher
`size=` mount, or fall back to building in `/dev/shm` which is usually
half of RAM and can be several GB.

## Don't do this

- **Don't `chmod 1777 /tmp` and hope.** Permissions aren't the issue.
- **Don't symlink `/tmp` to a persistent dir.** Some tools and
  sandboxing policies depend on `/tmp` semantics.
- **Don't `go clean -cache` to "free space" mid-build.** The cache is on
  the real disk; the failure is the tmpfs importcfg write.

## Last verified

- 2026-07-09 — `go-gitea/gitea` (Go 1.26.4) build on OpenClaw sandbox;
  `tmpfs 256M` mounted at `/tmp`; `TMPDIR=~/go-build-tmp` resolved the
  `importcfg: no space left on device` failures.