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

## Last Verified: 2026-07-08
