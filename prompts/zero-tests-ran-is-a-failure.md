# Zero-Tests-Ran Is a Failure, Not a Pass

**A checklist for any test suite that could be collecting zero tests while reporting success.**

A bounty issue asked for test coverage. The repo had a test file for it. The
harness reported green. The suite had **collected zero tests** — because the
file used `jest` globals in a project whose `test` script ran `vitest`. Every
assertion was dead code and nothing said so.

> Found 2026-10-22 on arakoodev/EdgeChains #290. Fix took the suite from
> **0 tests run to 17 passing** in under a minute.
> **Last verified:** 2026-10-22

## The Failure Mode

`jest.fn()`, `jest.mock()`, `describe/it` from a jest global scope, or bare
globals in an ESM-ish project do not error. They resolve to `undefined`, the
file is loaded, zero tests register, the runner exits 0. A coverage report
written at the same moment is 0% and looks like "no tests yet", not "tests
broken".

The three signals that distinguish this from a real pass:

| Signal | Real pass | Zero-ran pass |
|--------|-----------|---------------|
| Test count in output | `17 passed` | `0 passed` or count omitted entirely |
| Duration | tens of ms | single-digit ms, or instant |
| Coverage file | populated | 0%, or absent |

## Procedure

1. **Read the count, not the color.** `pytest -q`, `vitest run`, `jest` — every
   runner prints a test count. A green line with no number is not a pass.
2. **Match the framework to the runner.** Read `package.json` `scripts.test`
   or `pyproject.toml`/`pytest.ini`. A test file written for a different
   framework than the one the script invokes will silently collect nothing.
3. **Run one suite in isolation** before believing an aggregate count.
   `npx vitest run path/to/file` — if it collects 0, the file is the problem.
4. **Assert the count in CI**, not just the exit code:
   `vitest run --passWithNoTests=false` and a floor on the reported count.
5. **Ban cross-framework globals.** If `describe` is undefined, fail loudly.
   Add a smoke test that fails when the collector returns zero.

## Adjacent Case — Fake Credentials Turning Tests Green

The same suite also declared fake AWS credentials in its environment, made
live network calls, caught the failure, and fell back to an offline path. Every
test passed. Nothing was being tested.

Tells: a test that sets `AWS_*` / `*_TOKEN` to a literal, a mock that silently
degrades on exception, an assertion that only checks the function did not
raise. Offline suites should not need credentials at all — if one does, the
credential is load-bearing and the suite is testing your fallback, not your
feature.

## Anti-Patterns

- Treating exit code 0 as evidence tests ran.
- `|| true` in a CI test step, which converts the count into a decoration.
- Importing fixtures from a different framework because it "looks the same".
- `--passWithNoTests` in a project that is supposed to have tests.
- A test suite whose count nobody has read since it was written.

## Related

- `prompts/silent-failure-detection.md` — active probes vs state files that lie
- `prompts/silent-security-control-audit.md` — controls that degrade to no-ops
- `prompts/test-isolation-singleton-registry.md` — the other way tests lie (shared state)
