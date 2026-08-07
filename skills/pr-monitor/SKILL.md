# PR Monitor Skill

Watches open GitHub PRs for status changes and alerts via Telegram.

## What It Detects
- 💬 New comments from maintainers
- ✅ / 🔴 Code reviews (approved, changes requested)
- ✅ / ❌ CI check results (pass/fail)
- ✅ Merged PRs
- ❌ Closed without merge

## Files
- `pr-monitor.js` — core logic
- `pr-list.json` — PRs being tracked
- `pr-state.json` — last known state (auto-managed)

## CLI Usage
```bash
# Add a PR to watch
node pr-monitor.js add https://github.com/owner/repo/pull/123

# Remove a PR
node pr-monitor.js remove https://github.com/owner/repo/pull/123

# List tracked PRs
node pr-monitor.js list

# Check for changes (outputs JSON alerts or NO_CHANGES)
node pr-monitor.js check
```

## Token
Reads `hussain-alsaibai` token from `~/.git-credentials` automatically.
Override with `GITHUB_TOKEN` env var.

## Cron Integration
A cron job runs `check` every 2 hours and sends alerts to thread 17 (🚀 Projects).
