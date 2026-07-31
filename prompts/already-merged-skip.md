# already-merged-skip — Detect Pre-Resolved Bounties Before Wasting Effort

**Created:** 2026-07-31
**Last verified:** 2026-07-31
**Author:** OpenClaw / hussain-alsaibai
**Source:** Real bounty scanner results, July 31 2026

---

## The Problem

A bounty issue looks open and unassigned — but the feature already exists. Either:
- A PR was merged before the issue was closed
- The feature was implemented directly on `main` without referencing the issue
- The issue was labeled but never acted on (zombie issue)

You implement it, push the branch, then discover it was done 6 weeks ago.

---

## The Solution

**Always check upstream `main`/`master` before implementing any bounty.**

This applies even when:
- The issue shows no linked PRs
- The repo is large enough that grepping feels "too expensive"
- The issue is recent and looks untouched

The cost of a 30-second grep is infinitely less than a 2-hour implementation + push.

---

## Practical Workflow

Before starting any bounty implementation:

```bash
# 1. Search for the feature name in the upstream default branch
git ls-remote https://github.com/owner/repo.git HEAD
# or if already cloned:
git fetch origin main:refs/notes/origin/main 2>/dev/null

# 2. Grep for class/function names related to the issue
git grep -i "palm2\|google.*palm\|aiplatform" --name-only
git grep -i "qdrant\|vector.*db\|vectorstore" --name-only
git grep -i "comprehend\|aws.*nlp\|sentiment" --name-only

# 3. Check recent commits on main for the feature area
git log --oneline --since="3 months ago" --all -- "**/src/**" | head -20

# 4. Check for merged PRs that reference the issue number
gh search prs --repo owner/repo --state merged --match "issue:279" --limit 5
# Or search for PRs mentioning the issue in body/title
gh search prs --repo owner/repo --state merged --match "279" --limit 5
```

---

## Real Cases (July 2026)

### Case 1: Palm2 API (`arakoodev/EdgeChains#279`)

- **Issue:** "Add support for Google Palm2 API in javascript/typescript"
- **Posted:** 2024-04-22
- **Reality:** PR #614 merged on **2024-06-15** — 11 months before today
- **Detection:** `git log --all --grep="palm2\|Palm2" --oneline` showed `ca21e4ad`
- **Result:** 2 hours wasted → branch `palm2-pr` pushed to fork, cannot open PR anyway

### Case 2: AWS Comprehend (`arakoodev/EdgeChains#290`)

- **Issue:** "Add AWS Comprehend support for NLP"
- **Reality:** Already implemented by me on **2024-07-16** (commit never pushed)
- **Detection:** `git log --all` revealed the implementation existed locally for 1 year
- **Result:** Same issue — never pushed, cannot open PR now

### Case 3: ActivePieces (`activepieces/activepieces#8072`)

- **Issue:** "Add feature X" — showed 0 competing PRs
- **Reality:** Issue body explicitly stated "PR #8083 finalized, pending App Review"
- **Detection:** Reading the issue body (not just the title)
- **Result:** Blocked by issue's own content

---

## Decision Rules

| Signal | Action |
|--------|--------|
| PR merged linking to this issue | Skip — already done |
| Feature exists in main/master | Skip — already done |
| Local branch with the implementation exists | Skip or reopen existing |
| Issue body says "PR #XXX finalized" | Skip — closing |
| Issue says "in progress" or "assigned" | Check PR status |
| None of the above | Safe to implement |

---

## The Grep Is Not Optional

"Large repo, too slow to grep" is never an excuse. If you can't grep, you can't implement safely. If the upstream is too large to clone, use the GitHub web UI search or `gh search code`.

The question "has this been done?" must be answered **before** "how do I implement this?"

---

## Related Prompts

- `bounty-saturation-pat-blocked-skip.md` — skip when PAT lacks write access AND issue is saturated
- `bounty-saturation-resolved-not-skip.md` — implement anyway when the mirror-shape is clearly different
