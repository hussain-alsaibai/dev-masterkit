---
name: ci-target-must-match-repo-layout
description: Audit that CI actually runs the whole test suite and that the declared package version matches the module version. Trigger when a repo's CI badge is red for an unrelated reason, when a suite prints its dots and then hangs, or when a published package reports a version older than the code claims.
last_verified: 2026-10-24
---

# CI Target Must Match Repo Layout

## Why

A green CI badge and a shipped version number are both *claims*. Today, in
one repo triage, both claims were found to be false in the same day, across
nine repos:

- **5 repos** shipped a `pyproject.toml` version that lagged the module's
  `__version__` (`snapdb`, `fast-cache`, `tiny-cli`, `tiny-config`,
  `tiny-log`).
- **4 repos** ran CI against a hardcoded list of test files that named only
  *some* of the suite, leaving most of it invisible.

The second class is worse than a failing build, because a failing build is
loud. A CI job that names one test file **passes** while the rest of the
suite never runs. The badge is green and the coverage is a fiction.

The sharpest instance: `tiny-mcp-observability` shipped with **no test file
at all**, and its CI ran `pytest tiny_mcp_observability.py` — which collects
**0 items** and exits **5** (no tests collected). The badge was red for a
reason that had nothing to do with the module. Writing 35 tests then surfaced
three genuine bugs (see below).

The second sharpest instance: `tiny-agent-memory-v2`'s CI pointed at a
test file that did not exist, so the job errored on parse rather than on
behaviour.

## Procedure

### 1. Enumerate what should run, then compare to what CI runs

```bash
# What the repo actually has
ls test_*.py tests/test_*.py 2>/dev/null | sed 's|^|  |'

# What CI claims to run
grep -h -A2 'pytest|unittest|go test|npm test' .github/workflows/*.yml
```

Every test file in the first list must appear in the second. If a file is
missing from CI, the coverage it provides does not exist.

### 2. Prefer discovery over enumeration — but verify discovery works

```yaml
- name: Run tests
  run: |
    pip install pytest
    python -m pytest -v --tb=short
```

```yaml
- name: Run tests
  run: python -m unittest discover -s tests -v
```

Discovery is the default because an enumerated list is a snapshot that goes
stale the moment a file is added. **But discovery has its own failure mode:
it can collect zero items and still exit 0** — see
`prompts/zero-tests-ran-is-a-failure.md`.

### 3. Assert the count, so "zero tests" is a failure

```yaml
- name: Run tests
  run: |
    pip install pytest
    python -m pytest -v --tb=short
    # A suite that collects nothing must not pass silently.
    python -m pytest --collect-only -q | grep -q "test" || { echo "No tests collected"; exit 1; }
```

```python
# Or in-process: fail loudly when the collector returns nothing.
collected = runner.collect()
if not collected:
    raise RuntimeError("pytest collected zero tests — the suite is a fiction")
```

### 4. Keep the declared version and the module version in lockstep

```bash
grep -m1 '^version' pyproject.toml
grep -rm1 '__version__' --include='*.py' . | head -1
```

These must be equal. A lagging `pyproject.toml` means the **published
artifact reports an older version than the code it ships** — a silent lie to
every consumer who installs by version number.

### 5. Turn the version check into a test, not a convention

A convention is a wish. A test is a gate.

```python
def test_pyproject_version_matches_module():
    import tomllib, pathlib, re
    root = pathlib.Path(__file__).parent
    pyproject = tomllib.loads((root / "pyproject.toml").read_text())
    declared = pyproject["project"]["version"]
    src = (root / "tiny_log.py").read_text()
    module = re.search(r'__version__\s*=\s*"([^"]+)"', src).group(1)
    assert declared == module, (
        f"pyproject says {declared}, module says {module} — "
        "the published artifact would report the wrong version"
    )
```

This test is 8 lines and it closes a whole bug class permanently.

## The payoff, measured

Writing the missing test suite for `tiny-mcp-observability` surfaced **three
real defects** that had shipped undetected:

1. `defaultdict(Metric)` called `Metric()` with no arguments, but
   `Metric.name` is a required field — so **every** `end_span()` raised
   `TypeError`. Metrics were never recorded at all.
2. `export_spans()` passed raw dataclasses to `json.dumps(default=str)`,
   so exports were lists of Python reprs, not JSON objects.
3. `Observed.__call__` wrapped coroutine functions with a *synchronous*
   wrapper, returning an un-awaited coroutine. The span closed before the
   body ran, so **async failures were never recorded** and `error_rate`
   stayed `0.0` for every async call.

18 of the new 35 tests fail against the original module; all 35 pass after
the fixes. **A repo with no tests is not a repo with passing tests.**

## Pitfalls

- **A red badge is not proof the module is broken.** In
  `tiny-mcp-observability` the red badge was the *test target* being wrong.
  Read the CI log before blaming the code.
- **Do not "fix" a red CI by deleting the failing job.** That is the same
  error as deleting a failing test: it converts a visible failure into an
  invisible one.
- **@pyproject.toml` version drift is not cosmetic.** It is the number
  every consumer resolves against.

## Verification

- **Last verified:** 2026-10-24
- 9 repos audited; 5 with version drift, 4 with CI that did not run the
  whole suite, 1 with no test file at all.
- Fixed and verified by test run: `tiny-mcp-observability` (35 tests),
  `tiny-agent-memory` (CI path corrected), `tiny-cli` (1.2.0 + CI added),
  `tiny-config` (0.4.0), `tiny-log` (0.5.1), `tiny-validator`
  (all four test files), `tiny-agent-memory`, plus lint fixes in
  `tiny-safeexec`, `tiny-sandbox`, `tiny-workflow`.

## See Also

- `prompts/zero-tests-ran-is-a-failure.md` — the green-badge-that-collects-nothing case
- `prompts/reusable-ci-matrix-template.md` — the CI template this must be applied to
- `prompts/readme-claims-must-be-runnable.md` — the same principle applied to documentation
- `prompts/reentrant-lock-discipline.md` — the lock defect that a missing test suite hid
