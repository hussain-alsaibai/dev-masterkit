# A README code block is a claim with no executor

**First recorded:** 2026-11-09
**Last verified:** 2026-11-09 — 371 fenced ```` ```python ```` blocks extracted
from **62** published repositories (`tiny-*`, `snapdb`, `fast-cache`) and each
run in its own subprocess, `cwd` = the repo, `PYTHONPATH` = the repo, 25 s
timeout, no network. Results re-tabulated by hand per `(repo, block)`; the five
blocks that timed out are excluded from every rate below rather than counted as
passes.

This is the measured counterpart to
`prompts/readme-claims-must-be-runnable.md`, which states the principle from a
single repo (`fast-cache`). This file states the scale and the taxonomy, because
the taxonomy is what tells you which fix to apply.

## The measurement

| outcome | blocks | share |
|---|---|---|
| ran clean | 103 | 27.8% |
| fragment of a larger example | 214 | 57.7% |
| missing dependency | 22 | 5.9% |
| real code or doc error | **19** | **5.1%** |
| needs credentials / env | 5 | 1.3% |
| needs files or host paths | 3 | 0.8% |
| timeout | 5 | 1.3% |
| **total** | **371** | |

**Do not report 27.8% as "the docs are broken".** Most failures are honest.
The number that matters is the **19 real defects**, and every one of them lived
in a repository whose unit tests were green.

## The classification is the deliverable

Five of the seven buckets ask a different question, and only one of them is a
bug:

| bucket | what it means | the fix |
|---|---|---|
| ran clean | verified | none |
| fragment | continues an earlier block; can never run alone | none, but it was never verified either |
| missing dependency | the example needs The outside world | ship a fixture, or mark it |
| **real code/doc error** | the doc and the code disagree | fix one of them, then test the doc |
| needs credentials | unverifiable by design | mark it |
| needs files/paths | unverifiable by design | mark it |
| timeout | unbounded example | bound it or mark it |

A report that collapses these into one "pass rate" cannot tell the reader
whether to fix code, fix docs, or ignore the block.

## The 19 defects, grouped by shape

### A. The doc documents an API that does not exist (6)

| repo | README says | the class has |
|---|---|---|
| `tiny-router` | `@app.middleware` | `use()` only → `AttributeError` |
| `tiny-router` | `@app.websocket("/ws")` | `ws()` only → `AttributeError` |
| `tiny-eval` | `from tiny_eval import EvalSuite` | no `EvalSuite` |
| `tiny-event-emitter` | `emitter.on("evt", handler)` | `on()` requires positional `func` |
| `tiny-memo` | `bus.subscribe("evt", cb)` | `subscribe()` requires positional `callback` |
| `tiny-agent-toolkit` | `BudgetGovernor`, `IdempotencyGuard`, `DirectoryScratchpad` | none importable |

Six packages, three shapes, one cause: **the doc was written from the design
and the code shipped from the implementation, and nothing compared them.**

The `tiny-router` pair is the worst kind, because the decorator form is what
FastAPI uses. A reader who half-remembers FastAPI writes `@app.middleware` from
instinct, gets `AttributeError`, and blames themselves.

### B. Positional arguments in the wrong order (3)

`Response(401, {"error": ...})` against a `(body, status)` constructor produced
`body=b'401'`, `status={'error': 'Unauthorized'}` — **no exception, no warning,
a nonsense response at runtime.**

Every other HTTP library in the world is `(status, body)`. This is not findable
by reading; it is findable by running. Fix the *doc* to the keyword form, and
the ambiguity dies with it.

### C. Examples that need the outside world and do not say so (10)

`tiny-mcp-client` (connection refused), `tiny-llm` (401), `tiny-mcp-audit`
(assertion), `tiny-dist-audit` (needs a built `.whl` in `dist/`), `tiny-config`
(needs `config.production.yaml`), `tiny-budget-ledger` (needs
`/var/lib/openclaw`), `tiny-bloom` (`TypeError: 'ellipsis' object is not
iterable`).

Each is a *checkable* claim nothing checks: "point this at an MCP server",
"audit this wheel". **A README that requires a fixture should ship the fixture,
or the example is unverifiable forever.**

## Why the test suites could not see any of it

`tiny-router` had **196 passing tests**, including tests for `use()` and `ws()`.
The aliases were missing because **the doc was never a test input**. A unit test
exercises whichever of the two you wrote — it cannot find a disagreement between
them, because it only reads one.

## The procedure

1. **Extract every fenced block by fence language, not by eye.**
   `re.findall(r"```python\n(.*?)```", readme, re.S)`.
2. **Run each in its own subprocess.** Shared state turns block 4's success into
   block 5's `NameError`, and both results become fiction.
3. **Classify every failure into the seven buckets above.** Do it by hand; an
   automatic classifier will call `ImportError` and `ModuleNotFoundError` the
   same thing when one is a doc bug and the other is a missing dev dependency.
4. **Feed the survivors back as tests.** One test file per repo that executes
   the README's *primary* block verbatim, ~20 lines.
5. **Mark what cannot run.**
   `<!-- not-executed: needs a live MCP server -->` — so the next reader knows
   it was never verified, rather than assuming it was.

## The rule

> **A code example in a README is a claim, and a claim needs an executor.**
> Either a test executes the block, or the block carries a marker saying it was
> never executed.

Applied 2026-11-09:

- `tiny-router` 0.9.1 — `test_v091_documented_api.py::test_readme_middleware_section_runs_verbatim`
  re-executes the README middleware block, so the doc and the alias cannot drift
  apart again.
- Both new aliases (`middleware()`, `websocket`) are covered by that test, which
  is why the fix cannot be reverted by a cleanup.

## Sibling prompts

- `prompts/readme-claims-must-be-runnable.md` — the same rule from one repo,
  including the version-pinning trap (three clones, three versions).
- `prompts/a-binary-you-cannot-read-is-a-claim-you-have-to-check.md` — the
  release-artifact version of the same idea.
- `prompts/a-rule-must-pass-on-the-repos-own-fixture.md` — the dogfood half;
  that one lints the repo's own fixtures, this one executes its prose.
