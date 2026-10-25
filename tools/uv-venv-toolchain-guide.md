# uv + Virtual Environments — The Toolchain That Actually Works Here

**A verified reference for creating a Python environment on this container.**

> Found 2026-10-25 while setting up a test environment for
> `pipeshub-ai/pipeshub-ai#4650`. Three separate environment failures cost
> real time and each one looked like a dependency problem. **Last verified:**
> 2026-10-25 — `uv 0.13.5 (x86_64-unknown-linux-gnu)`, system Python 3.11.2,
> `/tmp` confirmed `tmpfs ... noexec`.

## The Three Facts That Decide Everything

| Fact | Value | Consequence |
|------|-------|-------------|
| `uv` version | 0.13.5 | `uv venv` + `uv pip install` is the supported path |
| System Python | 3.11.2 | the repo may require **3.12+** — see below |
| `/tmp` mount | `tmpfs ... noexec` | a venv under `/tmp` cannot load native extensions |

## Fact 1: `/tmp` Is noexec — Build the Venv Under `$HOME`

```
tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noexec,relatime,size=524288k,inode64)
```

A virtualenv created under `/tmp` installs fine and then fails at import
time with a message that does not mention the filesystem at all:

```
failed to map segment from shared object
```

That error reads like a broken wheel or a corrupt install. It is neither.
It is the kernel refusing to map a shared library from a **noexec** mount.

**Rule:** put the venv under `$HOME`.

```bash
# WRONG - installs, then fails on import with a confusing error
uv venv /tmp/venv && . /tmp/venv/bin/activate && uv pip install pydantic

# RIGHT
uv venv ~/venvs/project && . ~/venvs/project/bin/activate && uv pip install pydantic
```

Verify the mount before you debug anything else:

```bash
mount | grep -E ' /tmp | / '
# tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noexec,...)  <- noexec
```

This cost **three rounds of false failures** that each looked like a
dependency problem.

## Fact 2: `uv venv` + `uv pip install`, Not `python -m venv` + `pip`

```bash
# WORKS
uv venv ~/venvs/project
. ~/venvs/project/bin/activate
uv pip install -r requirements.txt

# FAILS - pip is not executable in the resulting environment
python3 -m venv ~/venvs/project
. ~/venvs/project/bin/activate
pip install -r requirements.txt
# -> /bin/sh: 1: pip: not found
```

`uv` also resolves and installs substantially faster, which matters when the
same environment is rebuilt in a loop.

## Fact 3: The Repo May Need a Newer Python Than the Container Has

`pipeshub-ai` requires **Python >= 3.12**. The container ships **3.11.2**.
Under 3.11 the test suite cannot even be *parsed*:

```
tests/conftest.py -> SyntaxError: f-string: expecting '}'
```

Nested same-quote f-strings are a 3.12+ feature (PEP 701). A 3.11 parser
rejects the file outright — so the failure looks like a broken test file
rather than a version mismatch.

**uv can fetch and manage the right interpreter:**

```bash
uv python install 3.12
uv venv ~/venvs/pipeshub --python 3.12
. ~/venvs/pipeshub/bin/activate
uv pip install -r requirements.txt
python --version   # Python 3.12.x
```

**Check the required version before installing anything.** It is in
`pyproject.toml` (`requires-python`) or `setup.cfg`:

```bash
grep -n 'requires-python' pyproject.toml
```

## The Standard Recipe

```bash
# 1. read the requirement first
grep -n 'requires-python' pyproject.toml || true

# 2. interpreter + venv, both under $HOME
uv python install 3.12
uv venv ~/venvs/<project> --python 3.12

# 3. activate and install
. ~/venvs/<project>/bin/activate
uv pip install -r requirements.txt

# 4. prove the environment works BEFORE running the suite
python -c "import pydantic; print(pydantic.VERSION)"

# 5. run the suite
python -m pytest <exact-target> -q
```

## Step 4 Is Not Optional

A venv can be created, populated, and still be unable to import the package
the project depends on — that is exactly the `noexec` failure. Prove the
environment with a real import **before** you conclude anything about the
code:

```bash
python -c "import pydantic_core; print('native ext OK')"
```

If that line fails, the problem is the environment, not the project.

## The CI-Target Rule

Run the **exact** target the CI workflow runs. A repo with no `tests/`
directory fails `pytest tests/` with "file or directory not found" — which
looks like a missing suite rather than a wrong path.

```bash
# read the workflow's pytest invocation, then run exactly that
python -m pytest <target-from-workflow> -q
```

See also `prompts/ci-target-must-match-repo-layout.md`.

## Verified Install (2026-10-25)

```bash
$ uv --version
uv 0.13.5 (x86_64-unknown-linux-gnu)

$ mount | grep ' /tmp '
tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noexec,relatime,size=524288k,inode64)

$ uv venv ~/venvs/pipeshub --python 3.12
$ . ~/venvs/pipeshub/bin/activate
$ uv pip install -r requirements.txt
$ python -c "import pydantic; print(pydantic.VERSION)"
```

Result: environment working, native extensions importable, and the suite ran
— **185 passed** (176 existing + 9 new).

## The Generalisation

> **Before debugging a dependency, prove the environment.** Three of the four
> failures recorded on 2026-10-25 were environment faults wearing a
> dependency costume: a noexec mount, a missing interpreter version, and the
> wrong venv tooling. Each one produced an error message that pointed at the
> wrong layer.

The order of operations that avoids all three:

1. check the mount flags for the directory you are about to use,
2. check the interpreter version the project requires,
3. build the venv with the tool that works,
4. prove an import works,
5. only then read the test failures.
