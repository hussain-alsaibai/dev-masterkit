# Skills pending AgentSkills frontmatter

Generated from the repository state on 2026-10-28.

A `SKILL.md` file is only loadable as an AgentSkill when it begins
with a YAML frontmatter block that declares at least `name` and
`description`:

```
---
name: my-skill
description: What this skill does and when to use it.
---
```

All 36 skills in this directory now carry that block, so every one of
them is loadable by an agent runtime. The backlog below is empty; it
is kept in the file so a future skill that arrives as a legacy markdown
document has an obvious place to be tracked.

`scripts/check_structure.py` fails the build if a file here stops being
a legacy document without gaining valid frontmatter, and warns while this list
is non-empty. Convert a skill by adding a frontmatter block; then remove it
from this list and the warning goes away.

## Pending (0)

_None. Every skill in `skills/` has valid frontmatter._

## Already loadable (36)

- api-dev
- api-retry
- api-validation
- benchmark-runner
- bounty-scanner
- bounty-verifier
- browser-automation
- ci-census
- browser-automation-stealth
- code-verify
- codebuddy-code
- credential-recovery
- cron-orchestrator
- data-analyst
- doc-generator
- docker-essentials
- duckduckgo-search
- fallback-notify
- github
- github-setup
- health-monitor
- human-actor
- mcp-duckgo
- model-cost-tracker
- oauth-helper
- pr-monitor
- prompt-engineering
- repo-creator
- security-audit
- security-sentinel
- test-automation
- working-memory
- youtube-analyzer
- youtube-api-skill
- youtube-transcript
- zero-dep-pattern
