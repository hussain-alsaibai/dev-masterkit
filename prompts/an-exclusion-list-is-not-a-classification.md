---
name: an-exclusion-list-is-not-a-classification.md
description: Use when a predicate, filter, or label decides a category by listing the values it is NOT — the values nobody listed silently land in whichever bucket the fallthrough happens to be.
---

# An exclusion list is not a classification

## The prompt

> Find every `if x not in (a, b)` that decides a category. Ask what the
> universe of `x` actually is. The values added after that line was written are
> already in the wrong bucket, and nothing reports them.

## What happened

`gortex` PR #1418, finding P2-5. The census labelled a tracked checkout
**unattributed** when `hasRecordedIntent` was false:

```go
func hasRecordedIntent(intents map[string]bool) bool {
    return intents["cli_track"] || intents["mcp_track"]
}
```

The intent universe is four kinds. Two of them — `manual_config` and
`project_membership` — were never named. So a checkout tracked purely by
`project_membership` fell through to *unattributed*, which is not merely a wrong
label: that bucket offers an auto-indexed heuristic and a remediation prompt, so
a correctly-tracked repository was told it was untracked and offered a fix for a
problem it did not have.

`project_membership` is **known provenance** — the repo belongs to a project the
user explicitly tracked. It is one of the strongest signals available.

**Fix:** `isManualConfigOnly` — a positive definition. Unattributed means the
intent set is exactly `{manual_config}`. `project_membership` alone is not
unattributed; `manual_config + project_membership` is not either.

## The rule

**When the definition is positive, implement it as a positive.** "Not in
{cli_track, mcp_track}" enumerates two of four kinds and treats the remaining
two as absent. "Only manual_config" states the actual condition and cannot
silently acquire new members when a fifth kind is added.

The failure mode is structural, not careless: an exclusion list is correct on
the day it is written and decays every time the universe grows. Nothing crashes,
no test fails, and the new value appears in a bucket that already has a name.

## The sweep

```bash
# every negative membership test that decides a label
grep -rnE 'not in \(|!.*in \[|!\s*has\(|!=\s*"[a-z_]+"(\s*\|\||\s*&&)' --include='*.go' --include='*.py' --include='*.js'
```

For each hit, answer three questions in writing:

1. **What is the full universe** of the tested value, today, and where is it
   declared? If it is a set/enum, the test should be written against the enum.
2. **Which member does the fallthrough produce**, and is that the safe answer?
3. **What happens when a new member is added** — does the new value land in a
   bucket that already exists, or does something fail loudly?

If (3) is "lands silently in a bucket with a name", rewrite it as a positive.

## How to verify

Build the fixture from the universe, not from the cases you were thinking of:

```
{manual_config}                        -> unattributed      (correct)
{project_membership}                   -> NOT unattributed  (was: unattributed)
{manual_config, project_membership}    -> NOT unattributed  (was: unattributed)
{cli_track}                            -> NOT unattributed
```

Run it against the **unfixed** tree first. Two of these four must fail there,
or the test is not aimed at the defect.

## Where this connects

- `prompts/a-redactors-escape-hatch-is-a-leak-when-the-scope-is-broader.md` —
  the same pass-through shape in a different function, found by the same
  reviewer in the same PR.
- `prompts/yaml-debug-tuple-unpack.md` — enumerating positions rather than
  names, in a parser.

---

**Last verified:** 2026-11-15 — finding P2-5 raised by the `gortex`
maintainer on `4a31f7a3e`; fixed on `doctor-legacy-state` (`e1185a5a0`), head of
PR #1418, MERGEABLE. Pre-fix harness reproduced 2 mislabelled intent sets,
post-fix 17/17.
