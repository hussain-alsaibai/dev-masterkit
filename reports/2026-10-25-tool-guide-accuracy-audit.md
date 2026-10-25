# Tool guide accuracy audit — 7 guides without a verification date

**Date:** 2026-10-25
**Scope:** the 7 tool guides in `tools/` that carried **no** `Last verified`
date, identified with `grep -L -i 'last verified' tools/*.md`.
**Method:** locate the local clone, **run its test suite**, compare the
measured result with the claim in the guide, and verify the upstream repo
exists.
**Last verified:** 2026-10-25 — every number below was produced by running
the suite, not by reading the guide.

## Why this audit exists

The 2026-10-23 audit corrected **35 of 90** guides that had drifted from
their code, using an import-and-symbol check. That check proves the *API
surface* matches. It does not prove the **counts** match.

So this audit asks a narrower, sharper question: **does the guide's headline
claim — "N tests passing" — survive running the suite?**

## Results

| Guide | Claim | Measured | Upstream | Verdict |
|-------|-------|----------|----------|---------|
| `tiny-agent-scope-guide.md` | 32/32 passing | **29 passed, 2 failed** | 404 (unpushed) | **WRONG — 2 real failures** |
| `tiny-skill-lint-guide.md` | 32/32 passing | **28 passed, 1 failed** | 404 (unpushed) | **WRONG — 1 real failure** |
| `tiny-event-emitter-guide.md` | 16 tests | **12 passed** | 200 | **WRONG — count** |
| `tiny-circuit-breaker-guide.md` | 12 tests | **25 passed** | 200 | **WRONG — count** |
| `tiny-tool-result-guide.md` | 51 tests | **51 passed** | 200 | correct |
| `tiny-skill-loader-guide.md` | 26/26 passing | **collection error → 23 passed, 2 failed** | 404 (unpushed) | **WRONG — suite did not run at all** |
| `dev-tools-comparison-guide.md` | (no test claim) | n/a | n/a | verified by content |

**5 of 7 guides made a false claim.** Two of the three upstream 404s are
repos that exist locally and have simply never been pushed — they are not
missing, so they were corrected, not deleted.

## The worst one: a suite that never ran

`tiny-skill-loader`'s test file contained a **literal newline inside a Python
string literal**:

```python
f.write_text("def register(reg, manifest
")
#                 ^ newline inside the string literal
```

`ast.parse` raised `SyntaxError` during **collection**, so pytest never
collected a single test:

```
ERROR test_tiny_skill_loader.py
!!!! Interrupted: 1 error during collection !!!!
1 error in 0.21s
```

The guide said "26/26 tests passing". The truth was **zero tests ran**, and
the exit status was a collection error — not a test failure. This is exactly
the 2026-10-22 lesson (*`prompts/zero-tests-ran-is-a-failure.md`*) recurring
in a repo whose guide claimed a green suite.

**Fixed on 2026-10-25** (commit `993ee9c` in the workspace repo). The suite now
collects and runs: **23 passed, 2 failed**. The two remaining failures are
real behaviour mismatches — the manifest-only `register()` fallback naming
and namespaced tool listing — and were left visible rather than papered over.

## The security-relevant one

`tiny-agent-scope` claims to enforce **denied hosts** and to fire an
`on_abort` callback. Both are broken:

```
FAILED test_tiny_agent_scope.py::test_url_host_denied
    with pytest.raises(ScopeViolation):
E   Failed: DID NOT RAISE ScopeViolation

FAILED test_tiny_agent_scope.py::test_context_manager_calls_on_abort
E   AssertionError: assert [] == ['aborted']
```

A **denied host is not denied**. For a library whose purpose is limiting an
agent's blast radius, that is the most consequential of the five wrong
claims — the guide describes a security control the code does not enforce.

Left as a documented, visible failure rather than fixed here: the correct
semantics (does a denied host raise on *use*, on *declaration*, or on
*request*?) is a design decision, not a one-line patch.

## Why the counts drifted

The counts were written when the code was written, and **nothing ever re-ran
the suite**. The guide's test count is a hand-maintained number in a prose
document, and prose does not fail CI.

Three of the five wrong counts are *over*-statements (16 vs 12, 12 vs 25 in
the other direction) and two are *under*-statements (32 vs 31). There is no
bias — they are simply **stale**, which is the argument for stamping them
mechanically instead of by hand.

## The Durable Fix (not applied by this audit)

> **A guide's test count should be generated, not typed.** The same rule as
> `prompts/spec-literal-must-be-generated.md`, applied to documentation: if a
> number can be produced by running something, produce it.

```bash
# the count in the guide should come from this command, in CI
python -m pytest -q 2>&1 | tail -1
```

A CI job that greps every guide for a test count and compares it with the
measured count would catch all five of today's errors automatically, forever.

## What was changed in the repo

- Each of the 5 wrong guides was corrected **in place** with the measured
  count and an explicit `Last verified: 2026-10-25` stamp.
- The two failures in `tiny-agent-scope` and the one in `tiny-skill-lint`
  are **stated in their guides**, not hidden — a guide that says "29 passed,
  2 failed" is more useful than one that says "32/32".
- `tiny-skill-loader`'s collection error was fixed and committed.
- **Nothing was deleted.** Per the 2026-10-22 rule, an unverified delete is
  the expensive direction of that error: two of the three missing upstream
  repos exist locally and are real.

See also `prompts/readme-claims-must-be-runnable.md`,
`prompts/zero-tests-ran-is-a-failure.md`,
`prompts/spec-literal-must-be-generated.md`.
