# Reserve Before You Work

**A rule for any agent that picks work from a shared issue tracker.**

> Found 2026-10-26 on `pipeshub-ai/pipeshub-ai#4753`. A scan at 07:08:30Z
> reported **competition 0, no assignee — CORRECT at that moment**. Work
> started at 07:09:44Z. At **07:17:10Z** — eight minutes later — another
> contributor, `wanjinhao1`, opened PR #4756 for the same target. At 09:03:03Z
> a maintainer assigned the issue to them. The scanner was correct and the
> work was still wrong. **Last verified:** 2026-10-26 — the 8-minute gap is
> measured from the live issue events, not inferred.

## The Shape of the Error

A scan is a **claim about the past**. Work is a **reservation of the future**.
Between the two is a window in which somebody else can claim the same thing.

```
  07:08:30Z   scan      -> "0 competing PRs, no assignee"   (true)
  07:09:44Z   work starts                                  <-- the window opens
  07:17:10Z   wanjinhao1 opens PR #4756                     <-- taken
  09:03:03Z   maintainer assigns #4753 to wanjinhao1
```

**Eight minutes.** No amount of scanning accuracy closes that gap, because the
scan is simply the wrong instrument for the job. A perfect scan of a stale
world is still a stale world.

The trap is that the failure looks like a *scanner bug*. It is tempting to
say "the scanner miscounted". The scanner did not miscount. The diagnosis
that gets logged is wrong, so the fix that gets written is wrong, and the
next occurrence is handled by the same wrong instrument.

> **The 2026-10-26 root cause was the 8-minute scan-to-work gap, not a
> scanner miscount.** The early "the scanner is wrong" reading was a
> misattribution — and it nearly sent the fix into the scanner instead of
> into the gate.

## The Rule

> **A scan is not a reservation. Re-verify live, immediately before work
> starts, and fail closed on anything you cannot measure.**

The gate is cheap. The scan is the expensive part and it is already done.
What is missing is a **fresh, narrow check** in the moment the work begins.

## The Procedure

1. **Re-verify the issue itself, live**, immediately before the first edit:
   - is it still open? (not closed / not completed)
   - does it have an assignee now? (`assignees` — the singular `assignee`
     field is honoured too)
   - does it say "comment here to claim"? → **claim it in a comment before
     writing code**, not after.

2. **Re-verify the competition count, live**, in the same moment:
   - count open PRs **by number reference** (`#4753` in the title or body)
   - **and by title similarity** — the competitor's PR title was
     `Add unit tests for docling_doc_to_blocks.collect_reachable_table_refs`
     and **did not mention the issue number at all**. Number-mention matching
     alone cannot see it.

   > The 2026-10-26 case is the specific reason title similarity is required:
   > PR #4756 targeted the same function and **the text contained no
   > "4753"**. A number-only detector reported 0 competition for a task that
   > was already being implemented.

3. **Fail closed on both checks.** If the issue state or the competition
   count **cannot be measured**, skip the candidate and move to the next one.
   Unknown is not zero. `daily-bounty-work.js` refuses to start on an
   unknown count, and that refusal is the correct behaviour.

4. **Make the gate a module, not a copy of the logic.** The first
   implementation wrote `reverify.js` and then **did not wire it into the
   worker**: `daily-bounty-work.js` neither required the module nor called
   it. The gate existed, was tested, and was not in the path.

   > **A gate that is not in the path is not a gate.** Wire it in, and make
   > the worker's refusal observable in its output.

## The Wiring Test

A gate module that is not imported is indistinguishable from a gate module
that does not exist. Test the wiring, not just the gate:

```js
// The integration check that was missing on 2026-10-26:
assert(
  dailyBountyWorkSource.includes("require('./reverify')"),
  'the worker must require the pre-flight gate'
);
assert(
  dailyBountyWorkSource.includes('reverify'),
  'the worker must actually call the gate before starting work'
);
```

The two failing checks on 2026-10-26 were exactly these two, and they were
the reason the fix was not considered done.

## The Generalisation

> **Anything you intend to act on must be re-checked at the moment of action.**
>
> A scan, a listing, a search result, a cached page — these are all
> **snapshots**. They are the right instrument for choosing. They are the
> wrong instrument for committing. Between the choice and the commitment,
> the world moves. Put a fresh, narrow, fail-closed check at the boundary.

This generalises past bounties: a file you were told to edit, a branch you
based on, a dependency version you resolved an hour ago, an issue you
selected from a queue. **Snapshot for choosing; re-verify for acting.**

See also `prompts/assigned-issue-is-a-taken-issue.md` (the assignee is the
claim) and `prompts/fail-closed-on-unavailable-data.md` (unknown is never
zero).
