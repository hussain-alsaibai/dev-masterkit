---
name: a-fix-that-changes-the-shape-of-a-predicate-has-new-wrong-cases.md
description: Use after a review says a predicate is wrong and the fix swaps one operator for another — exclusion for inclusion, count for membership, denylist for allowlist — because the new shape carries its own failure modes that the old fixture set never exercised.
---

# A fix that changes the shape of a predicate has new wrong cases

## The prompt

> You did not fix the predicate, you replaced it. The reviewer's reproduction
> now passes. What else does the new shape get wrong that the old one got
> right — and what did the old one get right that you have just dropped?

## What happened

`gortex` PR #1418, `hasRecordedIntent`. First review: the function asked "not
`cli_track` or `mcp_track`" against a four-member intent universe, so
`project_membership` — a strong provenance signal — fell through to
*unattributed* and was offered a remediation for a problem it did not have.

My fix swapped an **exclusion list** for a **positive test**, which is the
correct direction. But it implemented the positive test as a count
(`len(kinds) != 1`), and that count introduced a new wrong case:
`[]string{"manual_config", "manual_config"}` read as "not exactly one kind",
so a genuinely unattributed checkout was reported clean. The reviewer found it
in the next round.

**The first fix created the second bug.** Not by being wrong about the old
case, but by introducing a new premise — *one kind, one entry* — that the old
fixture set had no reason to test.

## The rule

1. **When a fix changes the operator, re-derive the truth table from the shape
   of the data, not from the failing example.** The failing example tells you
   which cell was wrong. It says nothing about the cells the new operator
   collapses.
2. **Write the four boundary inputs before the fix, not after:** empty,
   singleton, duplicate, mixed. Most predicate rewrites fail on duplicate or
   empty, because both look like "nothing interesting here".
3. **Carry the old fixture set forward unchanged.** If a case passed before and
   fails after, one of the two is wrong and you need to know which before a
   reviewer does. Here the earlier fix could have been silently weakened by
   "allow duplicates" = "allow anything"; the four mixed sets in
   `TestLegacyStateUnattributedExcludesMixedIntentRows` are what keep it
   honest.
4. **Say in the review reply which operator changed and why.** A reply that
   only reports the new reproduction passing invites a third round, because the
   reviewer cannot see the space you checked.
5. **Differential-test old vs new over a fixture set, and publish the table.**
   Same inputs, both functions, both columns. "New correct on 9/9, old wrong on
   2/9" is a claim a reviewer can re-run; "fixed" is not.

## Anti-pattern to recognise

```
if len(set(values)) != 1 { skip }   // "not uniform" -> skip the check
```

This is the exclusion list's error in a new costume: it treats *not belonging
to a single category* as *not belonging to the category that matters*. The
positive form is `all(v == category for v in values)`, with an explicit
`values` non-empty guard.

## Checklist before pushing the second attempt

- [ ] Truth table re-derived from the data shape, not from the failing input
- [ ] Empty, singleton, duplicate, mixed each have a test with an asserted
      *reason*, not just an asserted boolean
- [ ] Whole old fixture set still green
- [ ] Old function still available (in a harness, if not on disk) for the
      differential run
- [ ] Both columns of the table in the reply

---

**Last verified:** 2026-11-16 — this is the same PR (#1418) and the same guard
as `a-list-of-records-is-not-a-list-of-values.md`; two review rounds, two
distinct defects, both reproduced. Twelve `TestLegacyState*` tests in the file
at head `81fbce5c6`. The general lesson is much older than this PR — it is the
caller/predicate split AGENTS.md recorded on 2026-11-07 — but this is the first
case where the *fix itself* was the source of the next defect.
