# Report The Floor And The Ceiling Separately

**A capability census that averages the cheapest artefact with the rarest one
tells you nothing about either.**

> Found 2026-11-07 with a `git ls-files` sweep over the 65 `hussain-alsaibai`
> Python repositories that ship a `pyproject.toml`.
> **Last verified:** 2026-11-07 (12:00 EST) — counts below are from that sweep
> of cloned working trees, so **65 is a floor for our own corpus, never a
> claim about the ecosystem**.

## The rule

> **Publish the distribution, not the average.** "98% of repos have docs" is
> true, uninformative, and the same number at 5 repos and 500.

## The census

| artefact | present | note |
|---|---|---|
| README | 65 / 65 | free |
| `requires-python` | 65 / 65 | one line, no behaviour |
| CI workflow | 63 / 65 | `tiny-graph`, `tiny-mesh` |
| test file | 62 / 65 | same two, plus `mcp-server-registry` |
| LICENSE | 56 / 65 | **9 missing** — weakest of the cheap rows |
| validates a peer's capabilities | **1 / 65** | new as of today |

The top four rows are 85–100% and cost nothing to produce. The bottom row is
**1.5%** and costs an evening. Reported as one number, 89% of repositories are
"compliant", which is exactly the wrong sentence.

## Why the ceiling is the interesting number

Docs and a Python floor are *declarations*. They cannot be wrong in a way CI
would notice, because nothing executes them. The capabilities row is a
*behaviour*: it requires one repository to model another's contract and fail
when they disagree — the only row where the absence shows up as a runtime bug
instead of missing prose.

A census that ranks by "what is missing" will always recommend writing more
READMEs. Rank by **what would have to run** for the row to be true.

## The floor is a floor for the corpus, not the world

These 65 are **locally cloned** repositories. A repo not cloned is not counted
as missing — it is absent from the sample entirely. Write the denominator next
to the number (`65 cloned of N public`) or the census quietly becomes a claim
about GitHub.

## Checklist for the next census

1. State the sample and how it was selected — `git ls-files` over clones, not
   GitHub search.
2. One row per artefact, count and denominator, no averages.
3. Sort rows by *cost to fake*, descending — the bottom of the table is the
   report.
4. Re-run the whole census, not the interesting row, when anything is fixed.
