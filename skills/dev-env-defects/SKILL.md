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

**Last verified:** 2026-10-26 — every fact below was reproduced on this
container. `tiny-store` 24 tests pass, `tiny-graceful` 55 pass,
`tiny-mcp-observability` 35 pass, `tiny-mcp-skel` 43 pass,
`fast-cache` 108 pass.

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
