# Repo Discovery & Vetting

Systematic process for finding and vetting open-source repos for contribution.

## Usage

```bash
# Run discovery + vetting
node ~/.openclaw/workspace/skills/research/repo-discovery.js

# Output goes to stdout and is logged to daily notes
```

## Process

1. **Discovery** — Search trending repos by category (fintech, AI agents, security, automation)
2. **Vetting Checklist** (5 minutes each):
   - ⏰ Last commit within 30 days
   - ⭐ Stars > 100 (or active issues/PRs)
   - 📄 README has no political content
   - 🐛 Has open issues labeled `bounty`, `good-first-issue`, or `help wanted`
   - 📋 Issues have clear acceptance criteria
   - 🤖 Has `CONTRIBUTING.md` or `AGENT_CONTRIBUTOR_GUIDE.md`
3. **Rank** — Score by: payout, stack affinity, issue clarity
4. **Report** — Log top 3 to memory and Telegram thread 17

## Heuristics

| Signal | Action |
|--------|--------|
| `AGENT_CONTRIBUTOR_GUIDE.md` | ✅ Prioritize — DCO sign-off only |
| README references Israel/Palestine | ❌ Skip |
| No commits in 30 days | ❌ Skip |
| Bounty issues with system info requests | ❌ SCAM — skip |
| Every issue claims $7K+ on 5-star repo | ❌ SCAM — skip |

## Last Verified
2026-06-23
