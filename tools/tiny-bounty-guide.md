# tiny-bounty — Autonomous Bug Bounty Workflow CLI

## Repo
https://github.com/hussain-alsaibai/tiny-bounty

## One-liner
Zero-dependency CLI for AI agents to manage bug bounty targets, scoring, and task tracking.
Pure Python stdlib. JSON-based state. MIT.

## Install
```bash
pip install tiny-bounty
# Or: copy tiny_bounty.py directly
```

## Quick Example
```python
from tiny_bounty import BountyDB

db = BountyDB("targets.json")
db.add("https://github.com/example/repo", priority=8, bounty="$500")
db.list()
```

## CLI Usage
```bash
python tiny_bounty.py add https://github.com/example/repo --priority 5
python tiny_bounty.py list
python tiny_bounty.py score <id>
python tiny_bounty.py remove <id>
```

## Key Features
- Target tracking with priority scores
- JSON state persistence
- Agent-friendly (no external deps)
- Bounty URL + reward metadata

## Last Verified
2026-09-01
