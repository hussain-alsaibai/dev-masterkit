# CI that is not auto-triggered is CI that ran once, by accident

**Discovered:** 2026-11-11 (tiny-log `2ea3179`, tiny-cli 1.3.1 `1fe9955`)
**Last verified:** 2026-11-11 — both repos re-run with `pytest .` after the fix

## Two shapes, one cause

**A named-file list goes stale silently.** `tiny-log`'s workflow ran seven
files by name. `test_v080_text_extras.py` — the eleven regression tests for the
0.8.0 `extra=` fix — was never added to the list. The workflow was green for
the entire life of that file, because the file did not exist as far as CI was
concerned.

```yaml
# before — green forever, and means nothing
run: pytest tests/test_log.py tests/test_format.py ... (7 files)
# after
run: pytest .
```

**A per-file matrix hides cross-file state.** `tiny-cli` passed file by file
and failed as a suite: `_NO_COLOR` is latched once at import from `isatty()` +
env, and the test modules set `TINY_CLI_FORCE_COLOR` in their **module body**.
That only works if the module is imported before `tiny_cli`. Alphabetical
collection imports `test_completion.py` first, `_NO_COLOR` latches True, and
`TestColor::test_style` fails with `'31' not found in 'hi'`. The matrix ran one
file per command, so no run ever imported two modules into one process.

Fix: a `conftest.py` that sets the environment before any import, plus a job
that runs the suite in one process.

## The rule

> A test file that is not executed by CI is a draft, not a test.

Check the denominator, not the badge: `pytest --collect-only -q | tail -1`
against the number of files in `tests/`. A count that does not match is a file
nothing runs.

## How to verify the fix, rather than assume it

1. Run the suite the way a developer does: `pytest .` from the repo root.
2. Diff the collected count before/after. It must go **up** by the number of
   tests in the orphaned file.
3. Re-run the specific regression file alone — it should still pass, but that
   is not the proof. The proof is the one-process run.

## Cost

Both defects were found by running the suite rather than reading the workflow.
Neither was visible from a green badge, and one of them (tiny-log) was hiding
tests for a shipped bug fix.
