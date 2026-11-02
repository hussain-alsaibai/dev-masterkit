# tiny-skill-md Guide

> Zero-dependency SKILL.md parser, validator, renderer, and scorer. Pure
> Python stdlib. MIT. 556 LOC.

**Repo:** https://github.com/hussain-alsaibai/tiny-skill-md
**Version:** 0.1.0
**Last verified:** 2026-11-02 - **20 tests passing** (measured by run), CI
green. The repo **now exists upstream**; it returned HTTP 404 until
2026-11-02, and earlier versions of this guide said so.

## What It Is

A single-file library for parsing **SKILL.md** files (YAML frontmatter plus
markdown body), validating them, rendering them back to markdown, and
computing a heuristic quality score - without taking a PyYAML dependency.

```python
from tiny_skill_md import parse, parse_file, validate, score, discover

doc = parse_file("skills/my-skill/SKILL.md")
problems = validate(doc)
print(score(doc))
```

## API Surface

Verified by importing the module on 2026-11-02:

```
Issue, SkillDoc, parse, parse_file, validate, render_frontmatter, render,
score, discover, to_dict
```

**The parser is `parse` / `parse_file`.** An earlier version of this guide
documented `parse_skill`, which **does not exist** - that correction is
retained here because the name is the natural thing to guess.

| function | purpose |
|---|---|
| `parse(text)` | parse SKILL.md content into a `SkillDoc` |
| `parse_file(path)` | same, from a path |
| `validate(doc)` | return a list of `Issue` objects |
| `score(doc)` | quality score, 0-100, with a letter grade |
| `render(doc)` / `render_frontmatter(doc)` | round-trip back to markdown |
| `discover(paths)` | walk directories and find every `SKILL.md` |
| `to_dict(doc)` | plain-dict form, for JSON output |

`SkillDoc` is the parsed document; `Issue` is one validation problem with a
`level`, a stable `code`, and a message.

## Limits (module constants, verified by import)

```python
MAX_DESC_LEN          = 1024
RECOMMENDED_DESC_LEN  = 500
MAX_NAME_LEN          = 64
MAX_BODY_BYTES        = 256000
```

## Validation Codes

Extracted from the source on 2026-11-02, then **confirmed by running one
input per code**:

| code | meaning |
|---|---|
| `no_frontmatter` | the file has no YAML frontmatter block |
| `bad_yaml` | the frontmatter could not be parsed |
| `missing_name` | no `name` field |
| `missing_description` | no `description` field |
| `bad_name_type` | `name` is not a string |
| `bad_name_format` | `name` is not kebab-case |
| `bad_description_type` | `description` is not a string |
| `description_too_long` | over `MAX_DESC_LEN` (1024) |
| `description_head_long` | over `RECOMMENDED_DESC_LEN` (500) |
| `bad_version` | `version` is not valid semver |
| `bad_tags_type` | `tags` is not a list |
| `bad_triggers_type` | `triggers` is not a list |
| `bad_trigger_item` | an entry in `triggers` is not a string |
| `too_large` | the body exceeds `MAX_BODY_BYTES` (256000) |
| `empty_body` | no markdown body |

Two advisory codes are emitted at `info` level for structure quality:
`no_steps_section` and `no_verify_step`.

### The measured behaviour, which differs from the source reading

Running one input per code on 2026-11-02:

```
no_frontmatter         ['no_frontmatter', 'missing_name', 'missing_description', ...]
bad_yaml               ['bad_name_format', 'missing_description', ...]
missing_name           ['missing_name', 'no_steps_section', 'no_verify_step']
missing_description    ['missing_description', 'no_steps_section', 'no_verify_step']
description_too_long   ['description_too_long', 'description_head_long', ...]
bad_version            ['bad_version', 'no_steps_section', 'no_verify_step']
empty_body             ['empty_body']
bad_tags_type          ['bad_tags_type', 'no_steps_section', 'no_verify_step']
bad_triggers_type      ['bad_triggers_type', 'no_steps_section', 'no_verify_step']
```

Two things worth knowing:

- **`bad_yaml` did not fire** on malformed YAML. The parser is lenient; a
  broken frontmatter surfaces as `bad_name_format` and
  `missing_description` instead. **Read the codes that come back, not the
  ones you expect.**
- **Most inputs produce several codes at once**, because validation is not
  fail-fast. `description_too_long` also produces `description_head_long`
  (over 500 but under 1024). A single-fixture test per code therefore needs
  the fixture to be minimal.

That second point is the same trap as
`prompts/a-rule-that-cannot-fire-is-not-a-rule.md`: if you write a fixture
that trips three rules at once, you cannot tell which one fired.

## Packaging

```toml
requires-python = ">=3.8"
py-modules = ["tiny_skill_md"]
```

Verified by reading the upstream `pyproject.toml` on 2026-11-02.

## How It Differs From tiny-skill-lint

| | `tiny-skill-md` | `tiny-skill-lint` |
|---|---|---|
| role | parse / validate / **score** / render | **lint** with a code catalogue |
| codes | named string codes (`missing_name`) | numbered (`E001`-`E018`) |
| output | a `SkillDoc` and `Issue` objects | records with a level per code |
| score | yes, 0-100 with a grade | no |
| exit code | library | CLI, 1 on error - usable as a CI gate |

**They are complementary, not redundant.** Use `tiny-skill-md` to index and
rank a catalogue; use `tiny-skill-lint` as the CI gate.

## Related

- `tools/tiny-skill-lint-guide.md` - the linter (18-code catalogue)
- `tools/tiny-skill-loader-guide.md` - loading skills at runtime
- `tools/tiny-agentskills-guide.md` - the Agent Skills runtime conventions
