# A Gate Added After A Scan Has Not Been Tested On It

**Last verified:** 2026-11-21

## The prompt

> You just shipped a gate that rejects the candidate that got through. Before
> you call the bug closed:
>
> **1. Compare timestamps. Was the gate written before or after the artifact
> that motivated it?** `stat` the gate, `stat` the scan output. If the gate is
> newer than the scan, the scan never exercised it — the case that produced the
> bug is still the one case the gate has not seen.
>
> **2. Run the gate against the live input that failed, not a fixture you
> wrote afterwards.** Hand-written cases encode what you *remembered* about the
> failure. The live thread encodes what was actually there.
>
> **3. Assert on the evidence the gate reports, not just on its boolean.** A
> gate that says "rejected: already resolved" and quotes the wrong sentence is
> still broken — a human cannot audit it, and the next reader will believe the
> quote instead of the thread.

## What happened (2026-11-21)

A `commentsResolved()` gate was added to a bounty scanner at **02:12:27Z**
after a scan picked an issue that had already been fixed. The scan that
motivated it ran at **02:09:02Z** — three minutes earlier. **The gate had
never been run against the thread that produced it.**

Probed live against `Kc1t/alethe-agents#39` (6 comments fetched via `gh api`),
three things were wrong:

1. **The quote was the comment's first line, not the sentence that matched.**
   The verdict read `mapsiva: Hi Guys, tests matter for keeping software
   quality in check, ...` — the opener. The claim that actually fired
   (``the `tests/` directory this issue points to doesn't exist anymore``) was
   in the next paragraph. A verdict quoting the wrong sentence cannot be
   audited by the person reading it.
2. **A hedge two sentences later was invisible.** The same comment continues
   `If that already covers what this issue was asking for, happy to help close
   it out.` The gate tested only the sentence that matched, so the conditional
   never reached it.
3. **A plain "already working on it" reply fired.** `Since you are already
   working on those tests, I will not duplicate the effort` matched
   `already (fixed|resolved|done|closed)` — the word `already` was left as
   part of a phrase that reads as a resolution. The comment says the opposite:
   someone else is about to open the PR.

Fixes: quote the firing sentence (`findIndex(isAffirmative)`), widen the hedge
window to the **next two sentences**, and anchor the `already` pattern so it
needs a completion verb that is not preceded by `working on`. The live thread
still rejects — now quoting `humbertocg18: This looks resolved on 'main'.`
— and the three regressions are tests 8–10 of `test-resolved-gate.js`.

## The two rules underneath

**A green suite is not a tested gate.** All 7 original cases passed before the
probe, because they were written from the same memory that wrote the gate.
The live input is the only oracle for "did I fix the thing that happened".

**A rejection that quotes the right verdict and the wrong evidence is worse
than a wrong boolean.** The boolean gets fixed when it misfires. A plausible
quote gets believed.

## How to check any gate in one pass

```bash
# 1. ordering
stat -c '%y %n' <gate-file> <scan-or-report-that-failed>
# 2. live replay (read-only; gh uses the credential store)
gh api repos/OWNER/REPO/issues/N/comments --paginate > /tmp/live.json
node -e '/* extract the gate fn, feed it JSON.parse(require("fs").readFileSync("/tmp/live.json")) */'
# 3. both directions on the same body
```

Step 2 must show **the gate firing on the live case** and **not firing on the
hedged variants of the same body**. One direction proves nothing.

## Related

- `prompts/a-drift-test-can-measure-the-long-part.md` — coverage placed elsewhere
- `prompts/an-unclaimed-issue-is-not-an-unfixed-issue.md` — field-level checks miss timeline events
- `skills/verification-sweep/SKILL.md` — the family-wide re-probe procedure
