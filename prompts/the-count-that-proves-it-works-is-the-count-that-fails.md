# The count that proves it works is the count that fails

**Discovered:** 2026-11-11 (tiny-audit 0.2.0, `242b86b`)
**Last verified:** 2026-11-11 — 9 new tests run against 0.1.0 and 0.2.0 in the
same session: **9 failed on 0.1.0, 9 passed on 0.2.0**

## The claim

"Fixed" is a claim about two versions. A new test that passes on the fixed code
proves only that the fix does not crash on the case you thought of. The same
test, run against the **old** code with nothing else changed, is the only
evidence that it detects the defect — and it is the evidence most fixes never
produce.

Measured on `tiny-audit` this run:

| suite | 0.1.0 (defective) | 0.2.0 (fixed) |
|---|---|---|
| 9 new tamper tests | **9 failed** | **9 passed** |

A pass count alone reads as progress. The fail count is what makes it one.

## Why the temptation is strong

The old version is usually not checked out anymore. Reverting is annoying, the
container has the new files, and the test "obviously" targets a bug that
"obviously" existed. Every one of those is a reason to *believe* the test is a
regression test rather than a demonstration that it is.

The failure mode is silent and permanent: a test that passes against the broken
code becomes a green square in the suite forever, describing a bug it cannot
see. It is the test-side twin of `ci-that-is-not-auto-triggered-is-ci-that-ran-once`.

## Procedure

1. Write the test against the **fixed** tree and confirm it passes.
2. Get the old version without disturbing the working tree — `git stash`,
   `git worktree add /tmp/old <sha>`, or `pip install <old>` into a fresh venv.
3. Run the **same test file** against the old version. Every new test must fail,
   and the failure message must name the defect, not `ImportError` or
   `AttributeError` on a symbol that simply did not exist yet.
4. Record both numbers. "9/9 fail on 0.1.0" is the deliverable; "9 pass" is not.

## The trap this run actually hit

Two of the nine tests initially failed on 0.2.0 with an import error for
`AuditEntry.seq` — a field that only exists in the new version. They would have
"failed on 0.1.0" for a reason that had nothing to do with truncation. Rewritten
to build entries through the public constructor and assert on `verify()`'s
result, they detect the behaviour on both trees.

**A test that fails on the old version because a name is missing is not a test
that detects the bug.** Read the failure message; if it is an import or an
attribute error, the test has not reached the property yet.

## Where it applies

- A security fix (`verify()`, a sanitizer, an auth check).
- A guard whose whole purpose is to refuse something.
- Any bugfix whose test was written after the fix, which is nearly all of them.

The 2026-11-11 fleet survey found all four of the day's real defects in repos
with green CI. A badge reports that tests passed. Only the fail count against
the old version reports that the tests are about the bug.
