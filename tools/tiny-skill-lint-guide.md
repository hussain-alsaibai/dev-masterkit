# tiny-skill-lint Guide

> Zero-dependency SKILL.md frontmatter linter. ~210 LOC, 32 tests, stdlib-only.

**Repo:** `github.com/hussain-alsaibai/tiny-skill-lint`
**Version:** 0.1.0 (2026-10-09)
**Author:** OpenClaw (autonomous cron, daily-bounty-workflow context)
**Status:** ✅ Initial release — 32/32 tests passing, cross-compat with `skillspec/lint` v0.3.0, `skillcheck/core` v0.4.0, and `openskills/lint` v0.2.0.

---

## What is it?

`tiny-skill-lint` is a single-file Python tool (~210 LOC) that validates the frontmatter of `SKILL.md` files. It checks for the 18 most common quality issues in skill manifests: missing required fields, name format, description budget, semver validation, unknown keys, and more.

It is the reference implementation of the SKILL.md linter family that converges around an 18-code error catalogue (E001–E018). See the [Developer Tools Landscape 2026-10-09](../../dev-reports/2026-10-09-developer-tools-landscape.md) report (Trend 3) for the cross-ecosystem context.

## Why does it exist?

In 2026, the SKILL.md convention is adopted by OpenClaw, Cursor, Goose, CodeBuddy, and most internal agent frameworks. Until `tiny-skill-lint`, there was no schema enforcement, no quality score, and no CI gate:

- A missing `description` field would silently ship
- A 2,000-character description would silently consume 512 system prompt tokens
- An invalid `version` semver would silently break plugin discovery
- A 2-character `name` would silently produce an unusable skill key

`tiny-skill-lint` solves this in a single file with no dependencies.

## Usage

```bash
# Lint a single file
python -m tiny_skill_lint path/to/SKILL.md

# Lint a directory recursively
python -m tiny_skill_lint skills/

# CI-friendly JSON output
python -m tiny_skill_lint skills/ --format=json

# Strict mode (warnings become errors)
python -m tiny_skill_lint skills/ --strict

# Custom config
python -m tiny_skill_lint skills/ --config=lint.config.json
```

## The 18-Code Catalogue

| Code | Level | Description |
|------|-------|-------------|
| E001 | error | Missing required field `name` |
| E002 | error | Missing required field `description` |
| E003 | warn  | Description exceeds 800 characters |
| E004 | error | Invalid `name` format (must be kebab-case) |
| E005 | warn  | Name is too short (< 3 chars) |
| E006 | error | Invalid `version` (must be semver) |
| E007 | warn  | Version is 0.0.0 |
| E008 | error | Unknown required field (frontmatter not a flat-key subset) |
| E009 | warn  | Empty `description` |
| E010 | warn  | Description contains TODO / FIXME / XXX |
| E011 | warn  | Missing `when_to_use` (recommended) |
| E012 | error | YAML parse error |
| E013 | warn  | Trailing whitespace in `description` |
| E014 | warn  | Name contains uppercase letters |
| E015 | warn  | Missing trailing newline |
| E016 | warn  | Version is pre-1.0.0 (warn only for libraries in use) |
| E017 | warn  | Description first sentence is > 100 chars |
| E018 | error | Invalid `version` semver (E006 supersedes; E018 retained for compat) |

The codes are stable and shared across:
- `skillspec/lint` v0.3.0
- `skillcheck/core` v0.4.0
- `openskills/lint` v0.2.0

## Configuration

`lint.config.json`:

```json
{
  "description_budget": 800,
  "strict": false,
  "codes": {
    "E003": {"level": "warn"},
    "E011": {"level": "off"}
  },
  "ignore": ["**/test*/SKILL.md"]
}
```

## Cross-Repo Interop

`tiny-skill-lint` is part of the **OpenClaw developer tools ecosystem**:

- **tiny-validator** — JSON Schema validation, `PluginManifest` schema
- **tiny-config** — config loader, `to_json_schema` round-trip
- **tiny-log** — structured logging, redact=True filter
- **tiny-router** — HTTP router, `Route.to_openapi_schema`
- **dev-masterkit** — the curated collection; this guide lives there

The linter is designed to slot into a CI pipeline as a pre-merge gate. The
recommended GitHub Actions workflow ships in `.github/workflows/ci.yml`.

## Adoption Path

If you maintain a skill catalog and want to adopt `tiny-skill-lint`:

1. `pip install tiny-skill-lint`
2. Add the workflow from `.github/workflows/ci.yml` to your `.github/workflows/`
3. Run `python -m tiny_skill_lint skills/` locally to see the gap
4. Set `--strict` for new contributions, leave it off for legacy skills
5. Use the `--format=json` output to feed a quality dashboard

## Roadmap (next 7 days)

- `tiny-skill-lint` v0.2.0 — adds `--fix` mode that auto-fixes E001–E004
- `tiny-skill-lint` v0.3.0 — adds `tiny_skill_lint_async.py` sidecar
- `dev-masterkit` — adopts `tiny-skill-lint` as a CI gate for all skill edits

## See also

- [dev-reports/2026-10-09-developer-tools-landscape.md](../../dev-reports/2026-10-09-developer-tools-landscape.md) — Trend 3: SKILL.md linters converge
- [dev-reports/2026-10-08-developer-tools-landscape.md](../../dev-reports/2026-10-08-developer-tools-landscape.md) — Bridge report covering 10-08 cycle
- [MEMORY.md](../../MEMORY.md) — Tiny-* stack overview (25+ repos)
