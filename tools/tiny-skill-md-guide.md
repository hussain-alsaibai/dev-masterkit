# tiny-skill-md Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-skill-md
**Last verified:** 2026-09-22
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

Single-file SKILL.md parser, validator, renderer, and quality scorer — no PyYAML. Handles strict-subset YAML frontmatter (flat keys, scalars, lists, block scalars `|`/`>`, inline lists) with stable error codes and a heuristic quality score for ranking skill catalogs.

## When to use

Index, lint, and ship skill catalogs without taking on a YAML dependency. Built for OpenClaw's `tiny-agentskills` indexer and any agent framework using SKILL.md.

## Quick start

```python
from tiny_skill_md import parse_skill, validate, score

text = open("SKILL.md").read()
skill = parse_skill(text)             # strict-subset YAML frontmatter + body
errors = validate(skill)              # stable codes: missing_name, etc.
q = score(skill)                      # 0..1 heuristic quality score
```

## Key features

- **Zero deps** — pure stdlib
- **Strict-subset YAML** — flat keys, scalars, lists, block scalars, inline lists
- **Stable validation codes** — `missing_name`, `missing_description`, etc.
- **Heuristic quality score** — ranks catalogs
- **Render back to markdown** — round-trip support
- **Single file** — auditable in one sitting

## Integration pattern

Use as the front-end of any SKILL.md catalog: read → parse → validate → score → surface top N to agent system prompt. Pairs naturally with `tiny-agentskills`.

## Notes

- Created 2026-09-22 as part of the tiny-* ecosystem
- MIT licensed, zero dependencies
- Tests in `tests/`
