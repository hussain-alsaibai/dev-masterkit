# A compiler you cannot install is still a compiler you can verify with

**Added:** 2026-11-12
**Last verified:** 2026-11-12 (`gortex` v0.64.11 built on this container, 318.6 MB binary, `go test -run 'Doctor|Legacy' ./cmd/gortex/` → ok 2.063s)
**Class:** environment / build verification
**Cost of not knowing:** a PR that cannot run CI in its own repo is left unverified, when local evidence was one toolchain away

## The situation

A fork PR's workflows sit in `action_required` until a maintainer approves the
run — zero jobs, so the PR body's claim (`go test -run 'Doctor|Legacy' ./...`
passes) has **no evidence behind it from the author's side**. The container has
no `gcc`, no root, no `apt`. Building a Go module with cgo grammars looks
impossible.

It is not. `zig cc` is a C compiler you can install without root, and a
`CC` wrapper is enough.

```sh
CC="zig cc" CXX="zig c++" CGO_ENABLED=1 go build ./cmd/gortex
```

## Three failures that each look like something else

**1. cgo probes the compiler from stdin.** The probe runs
`zig cc -x c -` and reads the source on stdin. `zig cc` cannot read stdin, so
**every** package fails the probe and the errors look like a broken module tree:

```
build constraints exclude all Go files in .../bindings/go
```

The trees were fine. Fix: a wrapper script that rewrites the `-` argument to
`/dev/stdin` before exec'ing `zig cc`. One file, applied globally via `CC=`.

**2. An OOM looks like a parser crash.** `zig 0.13` dies silently on files
above ~50 MB. Of ~180 tree-sitter grammars, the only two that failed were
exactly the two largest source files (84 MB systemverilog, 65 MB nim) — which
reads like "these grammars are broken". `zig 0.15.2` fixed nim; systemverilog
still dies at **1.2 GB peak RSS**, which is a memory ceiling, not a syntax
problem.

**3. The Go linker needs `TMPDIR`, not just `GOTMPDIR`.** `/tmp` is a 512 MB
tmpfs. `GOTMPDIR` redirects the intermediate objects, but the link still writes
multi-GB files under `TMPDIR`, and the failure arrives **after** every grammar
has already compiled — `ENOSPC: no space left on device` at 100% of the work
done. Set both:

```sh
export TMPDIR=$HOME/tmp GOTMPDIR=$HOME/tmp
```

## What "verified" means here

- Binary built and runs: `--help` clean, `v0.64.11`
- The PR's own claim executed: `go test -run 'Doctor|Legacy' ./cmd/gortex/` → **ok** (2.063 s)
- The temporary stub added to make the build succeed **restored**, `git diff` empty, working tree clean

That third item is the part people skip. A build that needed a stubbed-out
parser is not a build of the branch; recording that the stub was removed and
diffed is what makes it one.

## The rule

**A missing system compiler is a toolchain problem, not a dead end — and the
first thing to suspect when cgo fails wholesale is the probe, not the code.**
Diagnose in this order:

1. Does the compiler pass a one-file probe outside the build? (`echo 'int main(){return 0;}'`)
2. Does it accept stdin? (cgo requires it)
3. Is the failure per-package or per-size? (size ⇒ memory/tmpfs, not syntax)
4. Is `TMPDIR` on a real filesystem with room for the link step?

**Second rule:** when CI cannot run, publish the local evidence *and* the
disclosure. "Verified locally with a zig cc wrapper; CI on the fork is
`action_required`" is honest and checkable. "Tests pass" from a fork with zero
green runs is not.

**Environment note for this container:** `xz` is not installed, so `.tar.xz`
downloads need `python3 -c "import lzma,tarfile; ..."` to unpack.
