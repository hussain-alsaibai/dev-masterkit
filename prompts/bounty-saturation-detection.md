# Bounty Saturation Detection

## Problem

GitHub bounty platforms (EdgeChains, Algora, Opire) get overrun by bot-generated PRs. Competing PRs sit open for days/weeks without merge, making them dead weight. A bounty that looks "open" is often a graveyard.

## Detection Criteria

**Skip a bounty repo entirely if ANY open bounty in it has >3 competing PRs.**

This is a repo-level saturation gate — not per-issue. If the repo has a hot bounty, assume ALL bounties there are ghost towns.

### EdgeChains Anti-pattern (Last verified: 2026-08-08)

| Bounty | Issue | Competing PRs |
|--------|-------|---------------|
| Palm2 API (JS/TS) | #279 | **11 open PRs** |
| Qdrant JS SDK | #273 | **7–9 open PRs** |
| Comprehend API | #290 | **8 open PRs** |

All three are on `arakoodev/EdgeChains`. Even though the Palm2 issue has no direct relation to Qdrant, the repo itself is saturated — skip the entire repo.

### Why >3 as the threshold?

- 1-2 PRs: Could be legitimate contributors or prior attempts
- 3+ PRs: High probability of bot farm activity, especially on bounty repos
- 4+ PRs: Definite saturation — ghost town pattern
- 11 PRs: Absolute no-go zone

## Scanner Implementation

```
For each repo in bounty search results:
  For each open bounty in that repo:
    pr_count = count_open_prs(repo)
    if pr_count > 3:
      saturation_score(repo) += pr_count  # penalize heavily

# Sort by saturation_score ASC (least saturated first)
```

Or simpler: `exclude_repos_where_any_bounty_has(pr_count > 3)`.

## Don't Confuse Saturation with Competition

- **Saturation:** Many PRs exist, none merged, repo is a ghost town → SKIP
- **Competition:** One or two PRs exist, could be legitimate → Evaluate on merit
- **Resolved-then-saturated:** A bounty was resolved (merged) but more PRs landed afterward → Use `merged_at` to detect; if any bounty merged within 7 days, the repo may be fresh → DON'T auto-skip

## Override Condition

If you have a **mirror-shaped** implementation (your PR is substantially different from existing ones — different approach, additional features, or fixing what others missed), you can override the saturation rule and open anyway. Document why the mirror shape exception applies.

## Last Verified

2026-08-11 — EdgeChains saturation re-check; Qdrant confirmed 7+ competing PRs, Palm2 11+, Comprehend 8+. Repo permanently saturated.
