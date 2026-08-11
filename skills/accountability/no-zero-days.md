# No Zero Days — Accountability Framework

Rule: Every day must produce at least one commit, one PR, or one shipped fix.

## Daily Check

Run at end of day (11 PM AST via cron):
```bash
node ~/.openclaw/workspace/skills/accountability/no-zero-days.js
```

## Enforcement

| If | Then |
|----|------|
| ≥1 commit today | ✅ Log success, move on |
| 0 commits today | 🚨 **EMERGENCY WORK SESSION** — pick smallest open issue, fix it, commit it |
| 0 commits 2+ days | 🔥 **ESCALATE** to The Architect |

## Emergency Work Session Protocol

1. Check `memory/YYYY-MM-DD.md` for today's planned work
2. If nothing planned: run bounty scanner, pick top non-scam issue
3. If no bounty issues: fix a typo in a monitored repo
4. If no repos: write a test, fix a lint error, update docs
5. **Ship before midnight AST**

## Why

- Consistency beats intensity
- A ship a day keeps the blockers away
- Zero-commit days compound into zero-progress weeks

## History
- Created: 2026-06-21
- Activated: 2026-06-23 (paired with daily cron)
