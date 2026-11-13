---
name: grep-every-copy-of-a-number-before-you-commit-the-correction
description: Use when correcting a count, version, or date in documentation — a corrected claim looks exactly like a verified one, and the stale copy two lines below wins the reader.
---

# Grep every copy of a number before you commit the correction

## The prompt

> You are correcting a number in a document. Before you commit:
>
> 1. Take the value being replaced and grep the whole file for it — the digits
>    alone, and every formatting of it (`48`, `48 dirs`, `**48**`).
> 2. Grep every *other* file that states the same fact. A stats table and the
>    prose about it are two copies.
> 3. Re-derive the new value from a command, and write the command next to it.
>    A number without its command is a number carried forward.
> 4. Confirm the arithmetic you are asserting (e.g. `49 - 44 = 5` and the five
>    named directories) actually closes, rather than repeating a previous
>    explanation that may have been wrong.
>
> Do not stop at the line you were asked to fix.

## Why

On 2026-11-13 the skills row in `dev-masterkit`'s README was corrected from
`48 dirs / 43 loadable` to `49 dirs / 44 loadable`. The correction was written
into the prose paragraph. The blockquote **three lines below it** still carried
the old numbers in a table — and a table reads as fact, while a paragraph reads
as commentary. A reader arriving at the blockquote takes the stale number.

The diff was reviewed line-by-line. Reviewing the lines you changed is exactly
how you miss the line you did not change.

## The shape it belongs to

This is the sibling of *a check that could not have run looks exactly like a
check that passed*. Same failure mode, different subject:

| Looks like | Actually is |
|---|---|
| a green CI badge | a workflow that never triggered |
| a passing linter | a different linter version |
| a corrected number | one corrected copy of it |

In all three, the artifact asserting correctness is real, and its counterpart
was never executed, or never swept.

## Verification

The fix is proven when `grep` for the old value returns only dated historical
entries — log lines that say *what the number was on that date* — and no live
claim. State that distinction in the fix: a changelog entry saying "Skills 48"
in the 2026-11-12 section is correct and must not be rewritten.

Last verified 2026-11-13 (`grep -n "48 / 43\|48 − 43" README.md` → matches only
dated log entries in the daily-updates history).
