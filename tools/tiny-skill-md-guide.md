# tiny-skill-md Guide

## Repo
https://github.com/hussain-alsaibai/tiny-skill-md

## One-liner
Zero-dependency SKILL.md parser, validator, renderer, and scorer. Pure Python
stdlib. MIT.

## Status
**Repo does not exist upstream yet** (`https://github.com/hussain-alsaibai/tiny-skill-md`
-> HTTP 404, checked 2026-10-23). Local clone only.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_skill_md import
parse_skill, validate, score`. **`parse_skill` does not exist.** Verified
against the local clone:

```
Issue, SkillDoc, parse, parse_file, validate, render_frontmatter, render,
score, discover, to_dict
```

The parser is **`parse`** (or **`parse_file`** for a path). `validate` and
`score` are correct. `SkillDoc` is the parsed document, `Issue` a validation
problem, and `discover` walks a directory of skills.

## Quick Example
```python
from tiny_skill_md import parse, parse_file, validate, score

doc = parse_file("skills/my-skill/SKILL.md")
problems = validate(doc)
print(score(doc))
```

## Key Features
- YAML-ish frontmatter parsing without a YAML dependency
- Validation producing typed `Issue` objects
- Round-trip rendering (`render_frontmatter`, `render`)
- Directory discovery for a skill tree
- 18 tests passing (verified by run, 2026-10-23)

## Related
- `tools/tiny-skill-lint-guide.md` — the linter (18-code error catalogue)
- `tools/tiny-skill-loader-guide.md` — loading skills at runtime
- `tools/tiny-agentskills-guide.md` — the Agent Skills runtime conventions
