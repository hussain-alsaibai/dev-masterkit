# tiny-bounty-workflow — Autonomous Bounty Workflow Engine

**Source:** [hussain-alsaibai/tiny-bounty-workflow](https://github.com/hussain-alsaibai/tiny-bounty-workflow)
**License:** MIT | **Language:** Python 3.9+ | **Last verified:** 2026-09-05

> State machine for autonomous bounty hunting. Scan → Score → Plan → Implement → Test → PR → Review → Iterate. Zero dependencies. ~500 lines.

## When to use

- Autonomous agents that hunt bug bounties on GitHub programmatically
- Agents that need to iterate on review feedback (not just submit one PR and stop)
- When you want a structured workflow with anti-scam filtering and scoring
- Lightweight alternative to commercial bounty platforms

## The Workflow

```
SCAN → SCORE → PLAN → IMPLEMENT → TEST → PR → REVIEW
                                              ↓
                                         ITERATE ←──────┐
                                              ↓           │
                                         (comments)      │
                                              ↓           │
                                         IMPLEMENT ─────┘
```

The iteration loop is the differentiator — most agents give up after the first PR.

## Quick Start

```python
import os
from tiny_bounty_workflow import BountyWorkflow, BountyScorer

scorer = BountyScorer(
    w_payout=0.30,
    w_competition=0.20,
    w_stack=0.25,
    w_clarity=0.15,
    w_freshness=0.10,
)

wf = BountyWorkflow(
    scorer=scorer,
    github_token=os.environ["GITHUB_TOKEN"],
    agent_languages=["python", "javascript"],
)

# Scan and score
bounties = wf.scan(query="bounty", min_bounty=50)
scored = wf.score_all(min_score=0.3)

# Run workflow
report = wf.run_top(max_bounties=2, max_iterations=3)
print(f"Merged: {report.merged}, PRs opened: {report.pr_opened}")
```

## Scoring Model

```
Score = w₁·payout + w₂·(1/competition) + w₃·stack_fit + w₄·clarity + w₅·freshness
```

| Factor | Weight | Normalization |
|--------|--------|--------------|
| Payout | 0.30 | min(payout/500, 1.0) |
| Competition | 0.20 | 1/(1 + prs/10) |
| Stack fit | 0.25 | 0-1 per agent |
| Clarity | 0.15 | Heuristic from issue body |
| Freshness | 0.10 | 1.0 for <7 days, 0.2 for >90 days |

## Anti-Scam Filters

Rejects bounties that are:
- High competition (>50 existing PRs)
- Expired (>90 days, no payout listed)
- New empty repos (<5 stars, <30 days old)
- Social engineering ("dm me", "contact on WhatsApp", "paypal me")
- Non-existent payouts (label says bounty, body says nothing)

## CLI

```bash
GITHUB_TOKEN=ghp_... python -m tiny_bounty_workflow scan --query "bounty" --min-score 0.3
```

## Integration with OpenClaw

```python
from tiny_bounty_workflow import BountyWorkflow
from tiny_agent_memory import TieredMemory

memory = TieredMemory(agent_id="bounty-agent-1")
wf = BountyWorkflow(scorer=scorer, github_token=token, memory=memory)

# Agent's memory survives restarts
bounties = wf.scan(languages=["python"])
for b in wf.get_top(3):
    memory.remember(f"Considering bounty: {b.title}", tags=["bounty", b.repo])
```

## Dependencies

**Zero.** Uses stdlib `urllib` for GitHub API calls.

## See Also

- [tiny-bounty Guide](tiny-bounty-guide.md) — v1 (CLI + JSON-based target tracking)
- [tiny-agent-memory-v2 Guide](tiny-agent-memory-v2-guide.md) — memory integration for multi-session continuity
