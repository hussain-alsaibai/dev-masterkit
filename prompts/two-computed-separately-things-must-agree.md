# Two Things Computed Separately Must Agree

**Last verified: 2026-11-24** — used to find and fix two defects in one day
(`tiny-log` 0.8.3 `04c74a1`, `tiny-validator` 0.7.4 `348695c`), both verified by
a REPL probe against the tagged source before the test was written.

## When to use it

Instead of grepping a codebase for a bug pattern by name ("`is not None` hit
test", "`len()` on an optional"), grep for **pairs of facts that are computed
in different places and are supposed to describe the same thing**. That class
of bug survives a fully green suite because each half is correct on its own.

## The invariant pairs

| pair | the disagreement looks like |
|---|---|
| **value ↔ unit** | unit chosen before rounding → `"1024.0 B"` |
| **required ↔ nullable** | absence expressible, null not; the `None` default rejects the document |
| **export ↔ import** | exporter emits `"nullable": true`, importer strips `"null"` |
| **branch ↔ default branch** | a fix lands on `main` the deploy never reads |
| **label ↔ payload** | a metric name says POST while the code reads GET |
| **schema ↔ writer** | on-disk row layout widened, reader not updated |
| **cache key ↔ lookup key** | stored as `"10"`, looked up as `"DEBUG"` |
| **count ↔ population** | `scored_count` counts post-gate survivors and reads as "nothing scored" |
| **pagination ↔ total_count** | the sweep reads one page and calls it the market |

Every row above has produced a shipped defect in this workspace. None of them
was found by a test; all of them were found by calling the function with the
input that separates the two halves.

## Procedure

1. **List the pairs.** Read the module's public functions and name, for each,
   what it *asserts about itself* twice (a value and its rendering, a schema and
   its exporter, a counter and the list it counts).
2. **Probe with one input per pair that makes the halves disagree.** That is
   the boundary (`1023.9999`), the sentinel (`None`, `inf`), or the round trip
   (import what you exported).
3. **Five lines, REPL, before writing any test.** The probe found the unit bug
   in under a minute on a tree whose 140 tests were green.
4. **Fix both halves, then add the test at the boundary.** A test near the
   boundary passes on the broken code.

## Why it beats bug-pattern grep

A pattern grep finds the bug you already fixed last time. An agreement
invariant finds the one you have not seen yet, because the *shape* is what
recurs: two computations, one of which was updated.

## Related

- `prompts/a-unit-chosen-before-rounding-contradicts-its-number.md`
- `prompts/nullable-is-a-field-fact-not-a-missing-value.md`
- `tools/probing-a-boundary-in-five-lines.md`
