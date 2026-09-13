# tiny-agentskills — Zero-Dep Runtime for Anthropic-Style SKILL.md Bundles

> Zero-dependency Python runtime for loading, parsing, and dispatching Agent Skills (Anthropic-style SKILL.md bundles).
> Last verified: 2026-09-11 | Version 0.1.0 | hussain-alsaibai/tiny-agentskills

## What It Is

A single-file Python runtime (~17 KB) that loads `SKILL.md` directories as agent-callable skills. No third-party deps — stdlib only.

- Parses SKILL.md frontmatter (name, description, triggers)
- Registers skills in a discoverable registry
- Dispatches invocations to skill procedures
- MIT licensed, 20 tests passing

## Why It Exists

- `agentskills.io` ships the catalog/spec, but no one ships the runtime
- Community treats SKILL.md as documentation only — this makes them **executable**
- Pattern: copy `tiny_agentskills.py` into any Python project, point it at a `skills/` dir

## Repo

https://github.com/hussain-alsaibai/tiny-agentskills

## When to Use

- You want to package expertise as a discoverable SKILL.md bundle
- You need a stdlib-only way to load skills into an agent loop
- You are building a skill marketplace/catalog runtime

## Install

```bash
pip install tiny-agentskills
# or copy tiny_agentskills.py directly
```

## Minimal Example

```python
from tiny_agentskills import SkillRegistry

registry = SkillRegistry("./skills")
skill = registry.match("summarize this thread")  # matches by description trigger
result = skill.run(context={"thread": thread_text})
```

## Tested Patterns

- Skill matching by trigger phrase (case-insensitive, substring)
- Frontmatter parsing (YAML subset)
- Registry hot-reload from disk
- Stdout JSON output for integration with cron/agent loops

## See Also

- `tools/tiny-mcp-server-guide.md` — exposing skills over MCP
- `prompts/system-instruction.md` — Vibe Coding session setup
