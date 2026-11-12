# Building Go With cgo Where There Is No System Compiler — zig cc on a Debian Container

**A verified toolchain reference for this container: no gcc, no root, no apt.**

> Found 2026-11-12 while verifying `gortex` (a Go+Treesitter project) from a
> fork whose CI could not run. Three separate failures each looked like a
> different problem. **Last verified:** 2026-11-12 — `zig 0.15.2`,
> `go 1.25`, `gortex v0.64.11`, 318.6 MB binary, `--help` clean.

## The Facts That Decide Everything

| Fact | Value | Consequence |
|------|-------|-------------|
| System compiler | **none** (`gcc`, `cc`, `clang` all absent) | any cgo build fails at the probe |
| `apt` / root | unavailable | cannot install a toolchain the usual way |
| `/tmp` mount | `tmpfs`, **512 MB** | Go's link step hits `ENOSPC` at the end of the build |
| `zig cc` | works, no root, single tarball | substitutes for gcc/clang directly |
| `xz` | **not installed** | `.tar.xz` needs `python3 -c "import lzma,tarfile"` to unpack |

## Step 1 — Install zig without root

Download the `linux-x86_64` tarball from `ziglang.org/download/`, then unpack it
with Python because `xz` is missing:

```sh
python3 - <<'PY'
import lzma, tarfile
with tarfile.open("/tmp/zig.tar.xz") as t:
    t.extractall("/home/node/opt")
PY
export PATH=/home/node/opt/zig-x86_64-linux-0.15.2:$PATH
zig version   # -> 0.15.2
```

**Pin the version.** 0.13 silently fails on source files above ~50 MB; 0.15.2
handles 65 MB. The version is part of the build description, not a detail.

## Step 2 — The stdin wrapper (the failure that looks like broken modules)

cgo probes the compiler by piping a C file on **stdin**:

```sh
zig cc -x c -      # zig cannot read stdin -> probe fails
```

Every cgo package then reports:

```
build constraints exclude all Go files in .../bindings/go
```

which reads as a broken dependency tree. It is not. Write a wrapper:

```sh
cat > /home/node/bin/zigcc <<'SH'
#!/bin/sh
args=""
for a in "$@"; do
  if [ "$a" = "-" ]; then args="$args /dev/stdin"; else args="$args $a"; fi
done
exec /home/node/opt/zig-x86_64-linux-0.15.2/zig cc $args
SH
chmod +x /home/node/bin/zigcc
```

Same wrapper with `zig c++` for `CXX`.

## Step 3 — Both temp variables, or the build dies at the last step

```sh
export TMPDIR=/home/node/tmp
export GOTMPDIR=/home/node/tmp
mkdir -p "$TMPDIR"
```

`GOTMPDIR` alone is **not enough**: the linker writes multi-GB object files
under `TMPDIR`, and on a 512 MB tmpfs the failure arrives after every grammar
has compiled — maximum work lost. See
`prompts/a-rerun-is-not-a-rerun-if-the-tempdir-was-full.md` for the pytest
version of the same trap.

## Step 4 — Build

```sh
CC=/home/node/bin/zigcc CXX=/home/node/bin/zigcxx CGO_ENABLED=1 \
  go build -o /home/node/gortex ./cmd/gortex
```

Result here: 318.6 MB binary, `./gortex --help` clean.

## The size ceiling is memory, not syntax

Two of ~180 tree-sitter grammars failed. Both were the largest source files
(84 MB systemverilog, 65 MB nim). Diagnose by size:

| Grammar | Source size | 0.13 | 0.15.2 | Peak RSS |
|---|---|---|---|---|
| nim | 65 MB | fail | **ok** | — |
| systemverilog | 84 MB | fail | fail | **1.2 GB** |

A per-file correlation is the signal. "These two grammars are broken" is not —
they were the two biggest files.

## When you stub a module to finish the build

Sometimes the only way to get a binary is to stub one parser out of the
registration list. That is legitimate **if and only if** you:

1. record the exact file and the stub,
2. restore it,
3. prove `git diff` is empty,
4. say in the report that the build used a stub.

An unreported stub makes the verification meaningless — you tested a build you
did not claim to have tested.
