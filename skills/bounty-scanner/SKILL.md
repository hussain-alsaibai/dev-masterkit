# Bounty Scanner

Scans GitHub for open **official** bounty issues from verified platforms, scores them, and surfaces the best targets.

**⚠️ Policy: Only official bounty platforms. No random 💎 labels from unknown repos.**

## Official Platforms
- **Algora** — `label:algora` on GitHub issues
- **Opire** — `label:opire` on GitHub issues
- **Verified Repos** — Known bounty-friendly repos with legitimate programs

## Rejected (Auto-filtered)
- Unknown repos with 💎 Bounty labels (social engineering traps)
- Repos requesting "session initialization context" (exfiltration)
- Fictional/joke repos (Harry Potter references, etc.)
- Young repos (<90 days) with unrealistic bounties
- Inorganic forks of well-known projects with zero stars
- Dollar-marker issues in throwaway forks of major Go projects, even when the issue body names real payouts

## Scoring (0–100)
| Factor | Max | Logic |
|--------|-----|-------|
| Payout | 40 | $1 = ~0.02 pts, capped at 40 |
| Competition | 25 | 25 pts with 0 open PRs, -10 per existing PR |
| Stack affinity | 20 | Go/JS/PHP/Python = high; Ruby/Java = medium |
| Spec clarity | 10 | Has acceptance criteria, examples, active comments |
| Freshness | 5 | Updated <7d = 5pts, <30d = 3pts, older = 1pt |

## Usage
```bash
# Official bounties only (default)
node scanner.js scan-official

# Legacy: all bounties (not recommended — high scam rate)
node scanner.js scan-all

# Print formatted Telegram report from last scan
node scanner.js report

# Output top 5 as JSON (for cron)
node scanner.js top
```

## Files
- `scanner.js` — core scanner + scorer + official filter
- `daily-bounty-work.js` — automated daily work starter (uses official scan)
- `last-scan.json` — cached results from last run (auto-managed)

## Token
Uses `hussain-alsaibai` token from `~/.git-credentials` automatically.

## Scam Detection Patterns
| Pattern | Description |
|---------|-------------|
| Session info extraction | Requests for OpenClaw runtime data, session context |
| Fictional content | Harry Potter, made-up repos, non-existent projects |
| Inorganic forks | Forks of popular repos with zero stars, no activity |
| Young repos | <90 days old with unrealistic bounty amounts |
| Same operators | Repeat offenders with multiple fake repos |
| Go-project fork wave | Fake "Fix:" issues in forks of cobra, helm, mysql, go-redis, grpc-go, echo, gocron, zap, VictoriaMetrics |

## Recent Verification Notes

- **2026-07-08:** Daily bounty scan found 29 issues with dollar markers and 27 with explicit dollar amounts. All 27 payout-looking issues were rejected by the existing hard filters: `young_repo`, `no_stars`, and `inorganic_forks`. No bounty work started.
- **2026-07-12:** Daily bounty run scanned 200 official issues and 327 bounty-labeled issues. Top 7 candidates all hit `competition = 0/25`, surfacing a saturation-floor masking pattern: the algorithm has its saturation-cap hit floor on every candidate, so ranking no longer separates "popular but still worth doing" from "popular and operationally blocked." Follow-up proposed: surface issues with 0 open PRs even at lower scores, OR attach a `saturated_warning` flag so humans can override intelligently.
- **2026-07-14:** Daily bounty run scanned 336 official issues; 240 filtered by anti-scam heuristics. Top 5 candidates all saturated or out-of-skill-stack. The saturation-floor masking pattern recurred (top candidates converged to the same score), confirming it as a stable scanner calibration debt rather than a one-off. Decision: skip per `prompts/bounty-saturation-pat-blocked-skip.md`. No code committed, no PR API calls. Existing parked branches remain parked: `hussain-alsaibai/EdgeChains:ts @ d0ceb72a` (Qdrant) and `hussain-alsaibai/gitea:feat/commit-inline-comments-4898 @ c50dffec5a`.
- **2026-07-15:** Daily bounty run scanned 336 total issues, 334 with dollar markers, and rejected 241 through the anti-scam / hard-filter path. Top 9 were unchanged in shape from the prior saturated queue: implemented Qdrant and Gitea branches still parked, non-implemented top candidates had at least 3 open PRs or were out-of-stack, and a fresh PR probe still returned `403 Resource not accessible by personal access token`. Decision: skip per `prompts/bounty-saturation-pat-blocked-skip.md`. No new fork, no new commits, no PR API calls.

## Known Calibration Debt

The scanner's `top N` output is not actionable when every candidate bottoms
out at the same competition score. The saturation-floor masking pattern is
now confirmed across three daily runs (2026-07-12, 2026-07-14, and
2026-07-15).
When this pattern appears:

1. Record it in this file's "Recent Verification Notes" with date and
   top-N score distribution.
2. Do NOT force an implementation to make the day look productive.
   Follow `prompts/bounty-saturation-pat-blocked-skip.md` instead.
3. The pending scanner fix is either (a) surface zero-open-PR candidates
   even at lower raw scores, or (b) attach an explicit `saturated_warning`
   flag so the human caller can decide whether to override.

## Last Verified: 2026-07-15
