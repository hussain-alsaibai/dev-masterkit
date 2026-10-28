---
name: ci-census
description: "Find every repository that has tests but no CI, or CI that cannot run the suite, and fix what it exposes. Use when auditing a fleet of repositories, when a package has tests but no workflow file, when a CI badge is red for a reason unrelated to the code, or when adding CI reveals defects nobody was checking for."
---

# CI Census

**Use when:** you own more than one repository, or one repository whose tests are
not being executed on every change, or a CI badge is red/wrong in a way that
does not name your code.

**Do not use when:** the error names a file and line of code you wrote. That is a
code defect, and `skills/dev-env-defects/SKILL.md` tells you how to triage it.

**Last verified:** 2026-10-28 — 25 repositories given their first CI workflow,
**8 real defects** found and fixed, all 25 green afterwards. Every test count in
this file was measured by run, on the oldest and newest matrix version.

## The Core Rule

> **A repository with tests is not a tested repository. The tests are a document
> until something executes them on every change, in the environment the package
> claims to support.**

On 2026-10-28, 25 tiny-* repositories had a test suite and **no workflow file
at all**. Adding one to each found 8 defects — including two libraries whose
central function could never run:

- `tiny-semantic-cache`'s `cosine_similarity()` raised `NameError` on **every
  call** (`sum(x * y for y in b)` — `x` is not in that generator),
- `tiny-ai-workflow` could not construct a single `WorkflowStep`, because
  `field(default_factory=None)` makes dataclasses **call** `None()`.

Every one of those repositories had shown a **green local test run** at some
point in its life.

## Procedure

### 1. Build the census

```bash
# every repo with a test suite
gh api 'search/repositories?q=user:<owner>+in:name&per_page=100' \
  --jq '.items[].full_name'

# for each: does a workflow exist?  does it name a test file that exists?
gh api "repos/<owner>/<repo>/contents/.github/workflows" --jq '.[].name'
ls test_*.py tests/test_*.py 2>/dev/null
```

Two separate lists:

1. **no workflow** — the backlog,
2. **workflow that does not run the suite** — worse, because it looks handled.

### 2. Derive the matrix from the package's own metadata

```bash
grep -n 'requires-python' pyproject.toml
```

Never guess the floor. Then check every stdlib call against the **oldest**
version in the matrix:

```bash
grep -rnE 'asyncio\.to_thread|cancel_futures|str\s*\|\s*None|\bstaticmethod\b' \
  --include='*.py' .
```

`tiny-scheduler` called `shutdown(cancel_futures=...)` (**3.9+**) while claiming
`>=3.8`. `fast-cache` called a `staticmethod` object, which is not directly
callable until **3.10**.

### 3. Name the test files that exist

```bash
ls test_*.py tests/test_*.py 2>/dev/null | sort
```

Either name those exact files in the workflow or use a bare `pytest`. A
hardcoded list that misses a file makes the badge a fiction.

**Watch for duplicate basenames.** `tiny-diff` and `tiny-eval` shipped
`test_tiny_diff.py` in both the repo root and `tests/`; pytest refused to
collect the second, and the `tests/` copy was stale.

### 4. Simulate CI exactly, before pushing

```bash
uv venv "$HOME/.venvs/probe-<repo>" --python <oldest>
VIRTUAL_ENV="$HOME/.venvs/probe-<repo>" uv pip install -e . pytest

# import from OUTSIDE the source tree
cd /tmp && "$HOME/.venvs/probe-<repo>/bin/python" -c "import <module>; print('OK')"

# run the workflow's own command
cd "$HOME/src/<repo>" && "$HOME/.venvs/probe-<repo>/bin/python" -m pytest <tests> -q
```

**Step 3 is the one that is skipped.** From inside the repo the loose source
file shadows the installed package, and a wheel that ships nothing importable
looks fine.

**Put the venv under `$HOME`, not `/tmp`.** `/tmp` here is a 512 MB **tmpfs**,
not the 16 GB disk; one venv per repo filled it mid-run and produced spurious
`No space left on device` failures that looked like build errors.

### 5. Read the outcome honestly

| outcome | what actually happened |
|---|---|
| `N errors` (collection) | **nothing ran** — the test module could not be imported |
| `N failed` | N assertions ran and were wrong |
| `0 passed` | the suite collected nothing — treat as a failure |

`snapdb`'s profiler bug produced **11 collection errors**, not 11 test failures.
The whole suite was unrunnable on two of five Python versions.

### 6. Fix the defect, then prove the fix

Run the suite on the **oldest** and **newest** matrix versions. If the defect
was environmental, the fix must be shown to survive a fresh environment.

## The defects this found, in one table

All eight, all real, all found by the procedure above:

| repo | defect | fix |
|---|---|---|
| `tiny-semantic-cache` | `sum(x * y for y in b)` → `NameError` on every call | `sum(y * y for y in b)` |
| `tiny-ai-workflow` | `field(default_factory=None, init=False)` → `TypeError` | `field(default=None, init=False)` |
| `tiny-file-watcher` | rename reported as `DELETED + CREATED` | keep an `inode -> last-seen-path` map |
| `tiny-scheduler` | `cancel_futures=` on Python 3.8 | guard with `sys.version_info >= (3, 9)` |
| `tiny-bucket-quota` | shipped `py-modules = ["tiny_rate_window"]` | ship the real module |
| `tiny-llm-router` | `py_modules` (wrong key) | `py-modules` |
| `tiny-jsonpath` | `package-data` with the empty-string key `""` | use a real glob |
| `tiny-diff`, `tiny-eval` | duplicate test basenames | remove the stale copy |

And a packaging class of its own: **five packages shipped wheels with no
importable module**, because

```toml
[tool.setuptools.packages.find]
include = ["tiny_semantic_cache*"]
```

finds nothing — a single top-level module is not a package. The fix is

```toml
[tool.setuptools]
py-modules = ["tiny_semantic_cache"]
```

## The race that hid inside a flaky test

`tiny-file-watcher`'s rename test failed **3 of 6** CI matrix jobs and passed
locally most of the time.

The first instinct is to lengthen the sleep. **That is not the bug.** `os.rename`
is **not atomic**: between the two halves there is a window where the old path
is gone and the new path does not exist yet. A scan landing in that window sees
a deletion; the next scan sees a creation. The move detector compared inodes
between *consecutive* snapshots, so the pairing was lost permanently.

The fix keeps an `inode -> last-seen-path` map, so a move is recovered one scan
later instead of being swallowed. Verified with a **400-trial** harness: 0
misses, where the old code missed 2–4 per 60.

The *test* fix was separate: the suite used a fixed `time.sleep(0.3)` against a
background polling thread. A **condition wait** returns as soon as the event
arrives and halves the suite time.

> **Reproduce the race before you fix the test. A longer sleep hides a real
> defect; a condition wait removes the flake without touching the library.**

## The workflow template that works

```yaml
name: CI

on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: pip install -e . pytest
      - name: Unit tests
        run: python -m pytest test_tiny_thing.py -v
```

Derive the matrix from `requires-python`. Name the test files that exist.

**Validate the file before pushing** — a YAML that does not parse produces a
run with **zero jobs**, which looks like a flaky runner:

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

See `prompts/validate-workflow-schema.md` for the full schema check.

## The generalisation

> **A repo with tests and no CI is untested in the only sense that matters.
> And a green local run is evidence about the source tree, not about the
> package.**

Eight of the twenty-five were broken in ways that made the library unusable.
None of it was subtle. All of it was invisible because **nothing executed the
tests in the environment the package claims to support.**

## See also

- `prompts/ci-census-reveals-what-was-never-checked.md` — the same procedure as
  a checklist
- `prompts/python-support-is-a-claim.md` — the declared floor is a promise
- `prompts/zero-tests-ran-is-a-failure.md` — a suite that collects nothing
- `prompts/ci-target-must-match-repo-layout.md` — CI must name the whole suite
- `prompts/validate-workflow-schema.md` — the workflow must parse
- `skills/dev-env-defects/SKILL.md` — when the failure is the environment
