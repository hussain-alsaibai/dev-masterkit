# Python Version Support Audit — 2026-11-03

**Trigger:** MakazhanAlpamys/Soup shipped `tests/test_requires_python_bound.py`,
which derives the `requires-python` ceiling from the CI matrix instead of
hardcoding it. It was the most useful engineering artefact in the day's
trending list, and it applies directly to us.

**Checker:** `dev-masterkit/scripts/check_python_support.py`
**Result:** 44 packages checked, 44 pass, 0 fail.

---

## What the check does

Compares the floor in `pyproject.toml` against the oldest Python in the
package's CI matrix, and fails when:

  * the floor is below the oldest version CI tests, so the declared support
    is untested; or
  * the package declares a floor and has no CI workflow at all.

A package with no Python source is skipped — the reports repos carry a
`pyproject.toml` so they can be installed as data, but there is no code that
could break on a version.

The check was verified to catch drift: lowering `tiny-semver`'s floor to
`>=3.7` makes it fail with "claims support for 3.7, but CI only tests 3.8 and
up", and restoring the file makes it pass.

---

## The first run: 20 problems in 44 packages

| kind | count | packages |
|---|---|---|
| floor below the CI matrix | 2 | tiny-agent, tiny-router |
| no CI workflow at all | 18 | tiny-agentskills, tiny-bloom, tiny-chain, tiny-checkpoint, tiny-context, tiny-diff, tiny-evaluator, tiny-inspector, tiny-llm-router, tiny-memory, tiny-rate-limiter, tiny-repl, tiny-retry, tiny-semver, tiny-sentinel, tiny-stream, tiny-tool-registry, dev-tooling-trends-2026 |

The 18 "no CI" packages were not merely untested — they had **never been
indexed** by CI. That is the same failure AGENTS.md already records from
2026-10-26: `tiny-log` declared `>=3.8` and called `asyncio.to_thread`
(3.9+). It shipped because CI was red and nobody read the badge. Except
there was no badge either.

---

## Three live bugs found

All three are the same defect: **PEP 585 builtin generics in a file with no
`from __future__ import annotations`**. `list[str]` is 3.9+, so on 3.8 the
annotation is evaluated at `def` time and raises `TypeError: 'type' object is
not subscriptable`.

| package | file | symptom |
|---|---|---|
| tiny-memory | `test_tiny_memory.py` | suite red on 3.8: `def fake_llm(msgs: list[str]) -> str` |
| tiny-cost-ledger | `tests/test_tiny_cost_ledger.py` | suite red on 3.8: `fired: list[tuple[AlertLevel, Period]] = []` |
| tiny-eval | `examples/regression_check.py` | example unparseable on 3.8 |

A sweep of every package confirmed only **three** files were affected; the
library modules all had the future import already. Only the test and example
files did not, because they are the files nobody opens.

All three fixed and verified: each suite fails on 3.8 before the change and
passes after, on both 3.8 and 3.11.

---

## Two more defects found while verifying

### tiny-repl: `current()` returned the wrong call

`ReplSession.current_step` is the index of the *next* call to run —
`step_forward()` reads the call at `current_step` and then increments it.
But `current()` returned `tool_calls[current_step]`, so before any
stepping it returned the **first** call. The REPL displayed a call the user
had not reached yet, and the CLI's "No current step." branch was
unreachable — which is why nobody noticed.

The second failing test was self-contradictory: it built a `ToolCall` with
`error="FileNotFoundError"` and then asserted `"not found"` was in the
error. The error string is stored verbatim, so the two can never both hold.

Fixed both. 25 passed on 3.9 (the declared floor) and 25 on 3.11; before,
2 failed on both.

### tiny-diff: a stale test file made the suite uncollectable

`tests/test_tiny_diff.py` was added with v0.1.0 and imports `diff_strings`,
`apply_patch`, `unapply_patch`, `diff_objects`, `apply_object_changes`,
`Patch` and `DiffHunk`. None exist in v0.1.2, so the file failed at import
and its module name collided with the root `test_tiny_diff.py`:

  ImportError: cannot import name 'diff_strings' from 'tiny_diff'
  ERROR: import file mismatch

pytest aborted collection, so the current 20-test suite never ran. The stale
file was removed (an independent session pushed the same fix to the remote
first, so the local commit was dropped in favour of theirs).

### tiny-skill-lint: a rule that could never fire

`_first_sentence()` capped its return at 100 characters, and the caller
tested `len(first) > 100`. The condition was always false, so E017 ("Description
first sentence is > 100 chars") was listed in the rule table and could never
be reported. The cap belongs in the caller, not the helper.

---

## CI added

16 packages gained a workflow, each with the matrix **starting at the version
`pyproject.toml` names**, because that is the version the claim is about.
Each was verified to pass locally at that floor before publishing.

| package | floor | tests at floor |
|---|---|---|
| tiny-agentskills | 3.8 | 20 passed |
| tiny-bloom | 3.8 | 22 passed |
| tiny-chain | 3.9 | (already had CI from another session) |
| tiny-checkpoint | 3.8 | 28 passed |
| tiny-context | 3.8 | 24 passed |
| tiny-evaluator | 3.8 | 26 passed |
| tiny-inspector | 3.8 | 38 passed |
| tiny-llm-router | 3.8 | 25 passed |
| tiny-memory | 3.8 | 73 passed |
| tiny-rate-limiter | 3.8 | 31 passed, 1 skipped |
| tiny-repl | 3.9 | 25 passed |
| tiny-retry | 3.9 | 34 passed |
| tiny-semver | 3.8 | 24 passed |
| tiny-sentinel | 3.8 | 34 passed |
| tiny-stream | 3.8 | 56 passed |
| tiny-tool-registry | 3.8 | 36 passed |

All ten whose workflow was pushed in this run are **green on GitHub**, and
each now runs Python 3.8 for the first time.

---

## Standing rule this establishes

**A `requires-python` floor is a claim, and the CI matrix is the only thing
that makes it true.** The three rules that follow:

1. **The matrix starts at the declared floor.** Not above it. If the floor is
   3.8, then 3.8 is in the matrix — otherwise the floor is a claim with no
   evidence.
2. **A package with no CI has no version claim.** It is not "probably fine";
   it is untested, and this repo has three packages where untested turned
   out to be broken.
3. **Any file that uses PEP 585 generics needs `from __future__ import
   annotations`.** The library module is not enough — the test files are
   where it was missed, three times, and the test files are the ones CI runs.
