# Bounty PR Finalized / Closed Skip

## Problem

The bounty scanner sometimes ranks issues that are **already resolved** — a PR was merged or finalized, but the issue wasn't closed on GitHub. The AI agent wastes hours implementing something that's already done.

Example: `activepieces #8072` (Gmail MCP, $200, 0 PRs per scanner) was actually finalized — PR #8083 was already merged, and the maintainer explicitly asked for no new submissions. The scanner missed this because it only looked at open PR counts, not the issue body itself.

## Detection Heuristic

Before pursuing any bounty, fetch the issue body and scan for these **finalized signals**:

| Signal | Example |
|--------|---------|
| PR merged | "PR #xxx has been merged", "This has been resolved in #xxx" |
| Maintainer request | "please do not submit", "no new submissions", "do not open a PR" |
| Closed/frozen | "This issue is closed", "frozen", "bounty closed" |
| Already done | "Already resolved", "implemented in", "shipped in" |

**Rule:** If any finalized signal is present, skip the issue regardless of score, competition, or payout.

## Scanner Integration (Last verified: 2026-08-12)

Scanner should perform a lightweight pre-check before scoring:
1. Fetch issue body via GitHub API (`GET /repos/{owner}/{repo}/issues/{number}`)
2. Run body through finalized-signal regex
3. If matched, set `score = 0` and add `finalized: true` flag
4. Skip in top-N output

```javascript
// Lightweight pre-check before full scoring
const FINALIZED_PATTERNS = [
  /PR\s+#\d+\s+(has been|was)\s+merged/i,
  /already\s+(merged|resolved|implemented|done|closed)/i,
  /please\s+(do\s+)?not\s+submit/i,
  /no\s+new\s+submissions?/i,
  /bounty\s+(closed|frozen|paid)/i,
  /this\s+issue\s+is\s+closed/i,
  /resolved\s+in\s+#\d+/i,
];

function isFinalizedIssue(body) {
  if (!body) return false;
  return FINALIZED_PATTERNS.some(p => p.test(body));
}
```

## Use Case

This check belongs in the bounty-scanner skill's `scanner.js`, as a pre-filter before the scoring phase. It adds ~1 API call per issue (negligible cost) and prevents wasted effort on dead ends.
