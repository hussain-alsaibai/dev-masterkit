# Grep for every use of the predicate you are replacing

**Last verified:** 2026-11-07

## The situation

A status rule was wrong: CI RED was assigned from "any failure in the last N
runs" instead of "the newest run on the default branch". The bug was real,
reported, and fixed — with a commit that introduced `latestBad`, rewrote the
summary line, and added the new field.

A day later the report was still wrong, in the same direction, on a brand-new
repository. The assignment line had never been touched:

```js
if (latestBad || failingRecent.length > 0) { status = 'RED'; }
```

The new value was computed. It was never *the* value.

## Why it survived

- Reading the diff showed a new predicate, a new summary field, and a message
  that matched the reported bug. The fix *looked* complete.
- The old predicate stayed in scope because it was still used for output
  (`recoveredCi`), so it was not dead code and no linter complained.
- The bug only fires on repos that fail and then recover quickly — rare in a
  steady-state fleet, common on a repo's first day.

## The procedure

1. **Name the old predicate before editing.** Grep it: `grep -n "failingRecent"`.
2. **Classify every hit**: value used in a status decision, or value used only
   for reporting. Anything in the first class gets rewritten in the same commit.
3. **Restate the rule as a single line** and check the source matches it
   literally. Here: *RED iff the newest completed run on the default branch
   failed.*
4. **Prove it with the case that failed** — a repo whose newest main run is
   green while older runs in the window are red.
5. **Report the old signal instead of deleting it**, renamed to what it actually
   means (`failingRecent` -> `recoveredCi`, superseded runs attached).

## The generalisable rule

> A fix that changes the *inputs* to a decision without changing the
> *expression that makes the decision* is not a fix. Search the file for the
> old input's uses; if it still reaches a status, you have shipped a comment.

## Counter-rule

> Don't refactor history into a boolean. A recovered failure is information. If
> the only way to make the fix is to delete the old signal, prefer renaming it
> and reporting it separately over folding `||` into a status field.
