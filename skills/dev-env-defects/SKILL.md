---
name: dev-env-defects
description: "Triage a failing install, build, or test as an environment defect rather than a dependency or code defect. Use when a package will not install, a venv will not import, a suite fails to collect, a binary will not execute, or a CI job dies for a reason that does not name your code."
---

# Dev Env Defects

**Use when:** an install, build, or test fails with an error that does not
name your code — a wheel that will not build, a venv that installs and then
cannot import, a binary that is "not found", a suite that collects nothing, a
CI job that dies before your code runs.

**Do not use when:** the error names a specific file and line of the code you
wrote. That is a code defect and the log already told you where.

**Last verified:** 2026-11-16 — collision trap added to *Other traps*: a bare
install name can resolve to a different author's package (six confirmed on
PyPI this session; `pip install tiny-cli` exits 0 and installs someone else's
CLI). Entry 1c added earlier the same day: a clean `go vet` on a tree whose
test files were never type-checked (missing `errors` import caught only after
stubbing four grammars on `gortex` #1418). Host facts re-checked: 198 cgo
files excluded, `gofmt -l` empty on changed files.

**Prior verification:** 2026-11-15 — two entries verified that run: the pytest
`-k` expression trap (a malformed filter runs *more* tests, never fewer, and
exits 0) and the `--doctest-modules` boundary (a docstring example has no name
predictable enough to filter, so scope by directory instead). Host facts
re-checked: `/tmp` still `noexec,size=524288k`; no `xz`, no `unzip`; `go test`
on a cgo project still excludes 198 files here, so `gofmt -l` + `go vet` on
only the changed files is the available signal, not a green suite.

**Prior verification:** 2026-11-14 — the checks below reproduced on two
repos whose long-standing "test failures" were entirely environmental.
MotionClone, both browser-related failures: **2 failed / 125 passed / 1
skipped** as shipped; `channel='chrome'` replaced by an `executable_path` for
**22/22 pass** on that one file; with a `HYPERFRAMES_BROWSER_PATH` set as
well the whole suite is **128 passed**. NullMotion: **27 / 27 pass** with
`TMPDIR` on the overlay, **2 fail** on the 512 MB tmpfs `/tmp`. *(An earlier
edit of this line claimed "NullMotion 27 → 36 / 36" and "MotionClone 15 fail
→ 0"; neither count was ever reproduced and both are withdrawn — see
`tools/static-toolchain-without-root-guide.md` for the measured table.)*
The 2026-10-26 facts
(`tiny-store` 24, `tiny-graceful` 55, `tiny-mcp-observability` 35,
`tiny-mcp-skel` 43, `fast-cache` 108 tests passing) still hold.

## The Core Rule

> **Prove the environment with a real execution before you read a test
> failure as a code failure.**

Three rounds of false failures on 2026-10-26 each wore a dependency costume:
`/tmp` is `tmpfs ... noexec`, so a venv built there installs fine and then
fails at import with `failed to map segment from shared object`; the repo
needs Python >= 3.12 and the container ships 3.11.2 (which cannot even
*parse* the conftest); and `python -m venv` + `pip` fails where
`uv venv` + `uv pip install` works.

**None of those was a dependency problem. All three read like one.**

## The Five Checks

Run these in order. Each is cheap and each eliminates a whole class.

### 1. Is there space, and where?
`/tmp` is a 512 MB tmpfs. On 2026-10-26 it was 86% full (438 MB) with
stale scratch dirs from a dead session. The original `npm install` failure
was **ENOSPC**, not a dependency problem.

```bash
df -h /tmp "$HOME"
mount | grep ' /tmp '
du -sh /tmp/* 2>/dev/null | sort -h | tail -10
```

**The venv must live under `$HOME`**, not `/tmp` — not only for space, but
because `/tmp` is `noexec`:

```bash
mount | grep ' /tmp '    # -> tmpfs ... noexec
```

### 1b. A test filter that runs MORE tests than you meant

`-k` evaluates a boolean expression over the test id; adjacent tokens are
implicit `and`. Two forms are wrong in ways that exit 0:

```bash
pytest -k "not slice long"       # not(slice AND long) -> excludes almost nothing
pytest -k "(not slice, not long)"  # syntax error in the expression
pytest -k "not (slice or long)"    # the correct exclusion of two things
pytest -k "not slice and not long" # also correct
```

The trap is silent in the safe direction: a bad filter **runs more**, never
fewer, so the run is green and the slow or environment-dependent modules you
tried to exclude are back in the count. Always read the collected line, or
resolve the expression without running anything:

```bash
pytest -q -k "not (slice or long)" --co | tail -1
```

Prefer paths (`pytest tests/unit`) or `norecursedirs` when excluding a
directory: `-k` matches by id substring and will hit a same-named test that
lives somewhere you did not intend.

### 1c. A clean `go vet` on a tree that never compiled your test files

`go vet` reporting **zero** does not mean your test files type-check. On a cgo
project with missing grammars, the package fails on build-constraint exclusions
**before** the compiler reaches `_test.go`, so `go vet` reports clean on a
package where a missing import would have shipped. Confirmed on `gortex`
2026-11-16: a missing `errors` import in a `_test.go` file survived a "clean"
vet. (This host excludes **198** cgo files; count your own with `go test ./pkg/
2>&1 | grep -c 'excluded'`.)

**Tell:** the claim is "vet was clean", but the package does not build. Run
`go build ./pkg/` — a failure under grammar exclusions is the signal.

**Fix shape — stub the blockers, compile, then restore:**

```bash
mkdir -p /tmp/bk && cp -r internal/grammar /tmp/bk/
# replace each failing grammar with a minimal stub that declares the types
# the package references, then:
go build ./pkg/ && go vet ./pkg/     # now type-checks _test.go too
cp -r /tmp/bk/grammar internal/      # restore
```

Four stubs (`cpp`, `swift`, `scala`, `kotlin`) were enough to reach the type
checker. **Restore from a backup and confirm `git status` is clean apart from
the files you meant to change** — a stub left in place compiles and lies.

**Report it as a limit, not as a pass:** "`go test ./cmd/x/` cannot run here
(N cgo files excluded); `gofmt -l` and `go vet` on the changed files are the
available signals, plus a harness with the functions copied verbatim." A green
vet presented as a green suite is the defect this entry exists to prevent.
See `tools/answering-a-review-when-the-fix-is-the-next-bug.md` §6.

### 2. Is the interpreter new enough to *parse* the repo?

A container on 3.11 cannot parse a 3.12 conftest. The error names a
*syntax* problem in a test file, and reads like a broken test file.

```bash
python3 --version
# The repo's real floor, from its own metadata:
grep -n 'requires-python\|python_requires' pyproject.toml setup.py 2>/dev/null
```

**Nested same-quote f-strings are PEP 701 — 3.12+.** If the conftest uses
them and you are on 3.11, the file is unparseable and the error is not about
your logic.

### 3. Is there a compiler?

```bash
for c in make gcc g++ cc; do command -v $c || echo "$c MISSING"; done
```

On this container all four are **MISSING**. A fresh `npm install` of
`better-sqlite3` cannot build from source here. GitHub Actions runners have
`build-essential`, so **CI works even though the local install cannot** —
which means a local failure is not evidence about CI and vice versa.

### 4. Are the shims executable?

```bash
ls -l node_modules/.bin/ | head
```

`node_modules/.bin` shims are **not executable** in this container, which
produces `prebuild-install: Permission denied` and `npm run lint` →
`eslint: not found`. Neither error mentions permissions.

**Workaround:** invoke the real entrypoint directly.

```bash
node node_modules/eslint/bin/eslint.js src/
```

### 5. Can you prove it works with a real execution?

Not a version check. An **actual import or execution**.

```bash
python -c 'import tiny_secret_mask; print("OK")'
node -e 'require("./src/server.js"); console.log("OK")'
```

**Prove it from OUTSIDE the source directory.** From inside, the loose
`.py` file shadows the installed package and masks the defect.

```bash
cd /tmp && python -c 'import tiny_secret_mask; print("OK")'
```

## The venv recipe that works here

```bash
# WORKS
uv venv "$HOME/.venvs/proj" --python 3.12
uv pip install --python "$HOME/.venvs/proj/bin/python" -e .
"$HOME/.venvs/proj/bin/python" -c 'import mypkg; print("OK")'

# FAILS here
python -m venv /tmp/venv && /tmp/venv/bin/pip install -e .
#  -> pip is not executable in the resulting environment
#  -> and /tmp is noexec, so the import fails with
#     "failed to map segment from shared object"
```

`uv 0.13.5` is the tool that works on this container.

## Other traps worth knowing

- **`TMPDIR` must be able to *execute* binaries, not just hold them, and it
  must not be small.** A test that writes a fake `ffmpeg` into
  `os.tmpdir()` and `spawn`s it fails with `EACCES` on this host, because
  `/tmp` is `noexec`. The failure surfaces as a **behavioural** assertion
  (`false !== true`) because the spawn error handler swallows it. Proven by
  running the identical fixture under `/home/node/.cache/tmp-exec`: exit 0,
  expected output. Use `TMPDIR=/home/node/.cache/tmp-exec` and note that
  `EACCES` \!= `ENOENT` — installing the binary changes nothing if the mount
  is `noexec`. Second failure mode on the same mount: `/tmp` is **512 MB**,
  and NullMotion's audio-extraction tests pass under the overlay `TMPDIR`
  and fail under `/tmp` — a passing suite under a chosen `TMPDIR` is a claim
  about that `TMPDIR`.
- **Playwright `channel='chrome'` wants a root-owned path.** `/opt` is root
  owned, there is no `sudo`, no user namespace (`unshare: Operation not
  permitted`), `CapEff: 0000000000000000`. `playwright install chrome` dies
  with `su: Authentication failure`. **`install chromium` does not need
  root**; if the suite hardcodes the `chrome` channel, fetch Chrome for
  Testing and point a fixture at it via `executable_path`.
- **npm 11 blocks install scripts by default.** `npm install` completes and
  **esbuild's** postinstall silently never runs, so the bundler cannot build
  and the failure appears three layers later. `npm install-scripts approve
  esbuild` (also `onnxruntime-node`, `protobufjs`). The `allowScripts` block
  npm then writes into `package.json` is an install-policy artifact — revert
  it before committing, it is not part of your change.
- **No `xz`, no `unzip`, no `tar` for compressed tarballs.** `.tar.xz` needs
  `python3 -c "import lzma,tarfile"`; `.zip` needs `python3 -m zipfile -e`.
  `tar xf` on a `.tar.xz` here dies with `Child returned status 2`, which
  reads like a corrupt download.
- **`pip install --target` extracts into `/tmp`, not `$TMPDIR`.** It fails
  `ENOSPC` while `df` shows 7.5 G free on the overlay. Set
  `TMPDIR=/home/node/.cache/tmp` (a real directory on the overlay) before pip.
- **`rm -rf` cannot clear a Go module cache.** The files are read-only, so it
  fails on thousands of headers and frees nothing. The correct call is
  `GOMODCACHE=<path> go clean -modcache` — and confirm the path is genuinely
  orphaned with `go env GOMODCACHE` first (2.0 G was reclaimed this way).
- **`package.json` `"allowScripts"` is not a real npm field.** npm ignores it.
  It only affects some other package managers.
- **`prebuild-install` fails with `ECONNREFUSED 127.0.0.1:80`** — its own
  local-mirror fallback. Not a network problem with npm.
- **A missing `eslint` config is not a lint error.** ESLint 9 requires a flat
  config (`eslint.config.js`); without one the lint script can never run.
- **A missing sibling package on PyPI is a CI defect.** `tiny-validator` is
  **not on PyPI at all** and `tiny-router`'s newest release there is `0.0.8`
  (while the pin wanted `>=0.7.0`). Install siblings from GitHub:

  ```yaml
  pip install "tiny-router @ git+https://github.com/hussain-alsaibai/tiny-router.git"
  pip install "tiny-validator @ git+https://github.com/hussain-alsaibai/tiny-validator.git"
  ```

  A hardcoded `/home/node` path in a test bootstrap is the same defect wearing
  a different hat — it makes the suite pass only on one machine.
- **A published name that belongs to a stranger is an install defect with no
  error message.** `pip install tiny-cli` exits 0 and installs TinyBio LLC's
  genomics CLI; `tiny-router`, `tiny-eval`, `tiny-queue`, `tiny-flags` and
  `snapdb` are the same (each checked against the PyPI JSON API on
  2026-11-16, six confirmed collisions). Nothing fails, so CI and the reader
  both pass. Check the registry **author**, not just the status code:
  `GET https://pypi.org/pypi/<name>/json` → `info.author`. Report `unknown`
  (429, timeout) separately from absent, or an outage reads as breakage. And
  read `git show origin/main:README.md` before fixing — three repos here were
  already correct remotely and only the stale clone held the broken line.
  Full procedure: `tools/install-line-audit-collisions-not-404s.md`.
- **A test file the workflow does not name is a test that never runs.** Two of the
  three repos touched on 2026-11-17 had a regression suite in the tree that CI could
  not see: `tiny-validator` never ran `test_v070_export_roundtrip.py` (14 tests),
  `tiny-config` never ran `test_v042_secret_heuristic.py` (9 tests) — each written for
  the release that fixed that very defect class. Nothing failed: the workflow was
  green and the file was committed. Check **both** directions with `comm` over
  `grep -oE 'tests/[a-z0-9_]+\.py' .github/workflows/ci.yml` and
  `ls tests/test_*.py` — a named path that no longer exists is the reverse defect.
  Same family as `testpaths = ["tests"]` pointing at no directory: collection is a
  claim about coverage. Full procedure: `tools/auditing-llms-txt-and-the-ci-test-list.md`.
- **A hand-written `llms.txt` is an unexecuted claim about the API.** The first file an
  agent reads before choosing a library, and the one file nobody tests. Three-way version
  equality (`Version:` = `pyproject.toml` = `__version__`), a **bidirectional** API list
  (documented => exported **and** exported => documented; the reverse direction is the
  only thing that catches a rename), and execute every snippet in a temp dir on the
  installed package. Proven against the previous files: 15 / 22 / 20 failures across
  `tiny-cli` / `tiny-validator` / `tiny-config`. Fixing them found three real bugs the
  57 existing tests had passed. Run the guard **before** fixing and record the count — a
  guard that has never failed is untested.

## The Procedure

1. **Read the error.** Does it name a file and line of your code? If yes, stop
   here — this skill does not apply.
2. **Run the five checks above.** In order. Space, then interpreter, then
   compiler, then permissions, then a real execution.
3. **Prove the environment** with a real import or execution, from outside
   the source directory.
4. **Only then** read the test failure as a test failure.
5. **Record the fix** as an environment fact, so the next run starts at step 1
   with the answer already known.

## The Companion Defect — the environment was fine, the *claim* was not

The inverse case is just as expensive. On 2026-10-26 a **real library bug**
was found while fixing CI:

```python
# BROKEN — an empty dict is falsy, so the caller's dict is discarded
self.hot = hot or {}

# CORRECT
self.hot = hot if hot is not None else {}
```

`tiny-store`'s `TieredStore` had **zero** `TieredStore` coverage in its
21-test suite. The bug shipped. Fixing it added 3 regression tests → 24.

**The environment was not the problem in that instance, and a triage skill
that always blames the environment would have hidden a real bug.** Both
directions happen. That is why step 4 exists: prove the environment first,
so that when you do reach the code, you know the environment is not the excuse.

## The Generalisation

> **A failing test is a claim about the system. Prove the claim before you
> act on it — and prove the environment first, because the environment is
> the cheapest thing to disprove and the easiest thing to blame.**

See also `prompts/python-support-is-a-claim.md` (the declared floor is a
claim you must test) and `tools/uv-venv-toolchain-guide.md` (the three
environment facts with their proofs).
