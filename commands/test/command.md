# /test Command

## Trigger

User types: `/test`, `/test <file>`, or "Run tests"

## Description

Runs the test suite and reports results. Automatically discovers tests or runs
specific test files.

## Usage

```
/test [path] [--verbose] [--failfast] [--coverage]
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | Specific test file or directory | Auto-discover |
| `--verbose` / `-v` | Verbose output | False |
| `--failfast` / `-f` | Stop on first failure | False |
| `--coverage` | Show line coverage (manual trace) | False |

## Workflow

1. **Discover tests** — `python -m unittest discover -s tests -p "test_*.py"`
2. **Run with options** — apply verbosity, failfast as requested
3. **Capture output** — stdout, stderr, exit code
4. **Parse results** — count passed/failed/errors/skipped
5. **Report** — summary table + failure details
6. **Suggest fixes** — for failures, offer to investigate

## Output Format

```
Test Results
============
Ran 42 tests in 1.234s

OK (42 tests)
  - test_normalize_url: PASS
  - test_empty_input: PASS
  - test_invalid_url: PASS
  ...

FAILED (2 failures)
  - test_edge_case_large_input
    AssertionError: expected 1000000, got 999999

SKIPPED (1 test)
  - test_windows_only_feature
    reason: Not on Windows

Coverage: 87% (manual trace)
  Missing: src/url_cleaner/utils.py lines 45-52
```

## Example

**User:** `/test --verbose`

**Result:**
```
test_normalize_url (tests.test_main.TestUrlCleaner) ... ok
test_empty_string (tests.test_main.TestUrlCleaner) ... ok
test_invalid_url_raises (tests.test_main.TestUrlCleaner) ... ok
...
----------------------------------------------------------------------
Ran 12 tests in 0.456s

OK
```

## Notes

- Uses stdlib `unittest` only; no pytest dependency
- If no tests found, offer to generate tests via `/test --generate`
- `--coverage` uses manual AST tracing (no `coverage.py`)
- Automatically sets `PYTHONDONTWRITEBYTECODE=1` to avoid `.pyc` pollution
