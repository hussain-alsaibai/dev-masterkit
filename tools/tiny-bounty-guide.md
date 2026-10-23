# tiny-bounty — Autonomous Bug Bounty Workflow CLI

## Repo
https://github.com/hussain-alsaibai/tiny-bounty

## One-liner
Zero-dependency CLI for AI agents to manage bug bounty targets and task
tracking. Pure Python stdlib. JSON-based state. MIT.

## Status
**Repo does not exist upstream yet** (`https://github.com/hussain-alsaibai/tiny-bounty`
-> HTTP 404, checked 2026-10-23). Local clone only.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_bounty import BountyDB`
with `db.add(...)` and `db.list()`. **There is no `BountyDB` class.** Verified
against the local clone:

```
TinyBounty(workspace: str = ".bounties")
  .add_target(repo_url: str, priority: int = 1)
  .list_targets()
```

The class is **`TinyBounty`**, the workspace argument is a **directory** (not a
JSON filename), and the methods are **`add_target`** and **`list_targets`**.

## Quick Example
```python
from tiny_bounty import TinyBounty

db = TinyBounty(".bounties")
db.add_target("https://github.com/example/repo", priority=8)
db.list_targets()
```

## CLI Usage
```bash
python tiny_bounty.py add https://github.com/example/repo --priority 5
python tiny_bounty.py list
python tiny_bounty.py remove <id>
```

## Key Features
- Target tracking with priority scores
- JSON state persistence under a workspace directory
- Agent-friendly (no external deps)

## Related
- `tools/tiny-bounty-queue-guide.md` — `tiny-bounty-queue` (scoring + dispatch, local only)
- `tools/tiny-bounty-workflow-guide.md` — `tiny-bounty-workflow` (anti-scam + scoring)
- `skills/bounty-scanner/SKILL.md` — the upstream scanner this ecosystem feeds
