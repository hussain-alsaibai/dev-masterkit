# Never Append Through a Whole-File Writer

**A safe-write procedure for agent tools whose write path replaces rather than appends.**

In OpenClaw code mode, passing `append: true` to the `write` tool does not
append. It replaces the entire file. It reports `changed: true` and raises no
error. Twice on 2026-10-22 it destroyed a 950-line module and a 494-line test
suite that had already been written and verified.

> **Last verified:** 2026-10-22 (two losses, ~20 tool calls to recover)

## The Procedure

1. **Write sections to separate part files**, never to the target:
   `part1.py`, `part2.py`, ...
2. **Concatenate with the shell:** `cat part*.py > final.py`
3. **Verify the count after every concatenate:** `wc -l final.py` against the
   sum of the parts. A mismatch means a part was dropped.
4. **Only then run the tests.** A silently-truncated module that still imports
   will pass a smoke test and fail later, somewhere less obvious.

## For Edits, Not New Files

`edit` has its own hazard: it reported `firstChangedLine: 84` against an anchor
that did not match what the file actually contained, and reported success.

- **Re-read the file after every `edit`.** Do not trust the reported line number.
- Anchor on text you just read from disk in *this* turn, not from memory of a
  previous turn.
- When an edit should produce exactly one hunk, `git diff --stat` should show
  one file with a small delta. A large delta means the anchor matched something
  you did not intend.

## Guardrails Worth Adding to Any Agent Setup

- Prefer patch-style writes over whole-file writes for appends, always.
- Take a `git stash`/commit before a multi-step write session on an untracked
  file — a commit is the only undo that is actually reliable.
- If a file shrank unexpectedly, assume truncation before assuming a bad edit.
  Check `wc -l` against the last known count first.

## Why This Belongs in a Dev Toolkit

The general rule: **a tool that reports success is claiming it did what you
asked, not that the result is what you meant.** Any write path that can
silently substitute a different operation needs a verification step bolted on
at the call site, because the tool cannot know your intent.

The same class of defect is what `prompts/silent-failure-detection.md` and
`prompts/silent-security-control-audit.md` describe from the runtime side.
