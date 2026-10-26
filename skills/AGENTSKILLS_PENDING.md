# Skills pending AgentSkills frontmatter

Generated from the repository state on 2026-10-26.

A `SKILL.md` file is only loadable as an AgentSkill when it begins
with a YAML frontmatter block that declares at least `name` and
`description`:

```
---
name: my-skill
description: What this skill does and when to use it.
---
```

The files below are legacy markdown documents. They read fine as documentation
but an agent runtime will not load them as skills, so they are not discoverable
by anything that follows the AgentSkills convention.

`scripts/check_structure.py` fails the build if a file here stops being
a legacy document without gaining valid frontmatter, and warns while this list
is non-empty. Convert a skill by adding a frontmatter block; then remove it
from this list and the warning goes away.

## Pending (25)

- [api-dev]
- [api-retry]
- [api-validation]
- [benchmark-runner]
- [bounty-scanner]
- [browser-automation]
- [browser-automation-stealth]
- [code-verify]
- [cron-orchestrator]
- [data-analyst]
- [doc-generator]
- [duckduckgo-search]
- [fallback-notify]
- [health-monitor]
- [human-actor]
- [model-cost-tracker]
- [pr-monitor]
- [prompt-engineering]
- [repo-creator]
- [security-audit]
- [security-sentinel]
- [test-automation]
- [working-memory]
- [youtube-analyzer]
- [zero-dep-pattern]

## Already loadable (10)

- bounty-verifier
- codebuddy-code
- credential-recovery
- docker-essentials
- github
- github-setup
- mcp-duckgo
- oauth-helper
- youtube-api-skill
- youtube-transcript
