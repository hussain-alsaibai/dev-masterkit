# A delta measured against a stale baseline is zero by construction

**Last verified:** 2026-11-10

## The situation

The repo health sweep reports `starsGained24h` and `starsLost24h` next to real
numbers: 175 repos, 174 green, 1 yellow, 0 failing CI. Those are measured this
run and they move. The star deltas were computed against
`previousCheck 2026-11-10T13:05:31Z` while `checkedAt` was
`2026-11-10T17:00:23Z`.

A delta between 13:05 and 17:00 is a **four-hour** window. It was published as
a **24-hour** figure. Both came out `0`, and a zero that cannot move reads
exactly like "nothing happened".

## Why it is invisible

A bounded window does not error. It produces a smaller number — usually zero —
and zero is the value a quiet day is supposed to have. Nothing in the JSON
distinguishes:

- "no one starred the repos in the last day", from
- "the baseline I subtracted was taken two hours before the comparison started"

The report carried both timestamps the whole time. Nobody subtracted them.

## The rule

**Before publishing any delta, print the two timestamps it was computed from
and check the interval is the one the label claims.** If the baseline is
older or newer than the window, either re-baseline or relabel the number —
`starsGained4h` is honest; `starsGained24h` over four hours is not.

Practical form: compute `checkedAt - previousCheck` and assert it is within
tolerance of the labelled period. A one-line guard turns a wrong number into a
failed run.

## What to do with the value in the meantime

Say the measurement did not happen. "No change recorded either way" and
"today's star delta is effectively 0-by-construction" are both honest; a bare
`0` under a `24h` heading is not. When a metric is about to gate a decision,
re-baseline first — a fabricated zero is worse than a missing number, because
it argues for doing nothing.

## Adjacent case, same day

`checkedAt - previousCheck` also decides whether a "stale but success" CI run
is a failure. A green run 9-12 days old is a **cadence** signal, not a red
badge (see the 2026-11-06 rule). Both bugs are the same bug: an interval that
was never compared to the claim attached to it.
