# tiny-skill-lint Guide

> Zero-dependency SKILL.md frontmatter linter. 329 LOC, 38 tests, stdlib-only.

**Repo:** `github.com/hussain-alsaibai/tiny-skill-lint`
**Version:** 0.3.0 (branch `fix/e019-dogfood`, commit `d2e70d9`)
**Last verified:** 2026-11-09 - **38 tests passing**, `E019` added, dogfood
step fixed and re-run locally (see *E019* below). `main` is still 0.2.0; the
0.3.0 work is open in PRs #2 (feature) and #3 (dogfood fix, stacked).

## E019 — `name` must match the parent directory name

The most plainly stated rule in the agentskills.io spec, and the linter was
missing it until 2026-11-08. A skill directory `foo/` must contain a SKILL.md
whose frontmatter declares `name: foo`; kebab-case on the basename is not
enough (that was E004).

| Code | Level | Description |
|---|---|---|
| E019 | error | `name` does not match the parent directory name |

**It shipped green and broke CI on the repo's own fixture.** The branch passed
38 unit tests and a mutation check; the failing step was the **dogfood** step,
which lints `examples/`:

```
examples/SKILL.md
  E019 [error] 'name' (skill-authoring) does not match parent directory (examples)
```

Fixed by moving the fixture to `examples/skill-authoring/SKILL.md` — the shape
the spec requires and every real bundle has. **Run the linter against
`examples/` before calling a new rule done**; it takes one second and no unit
test in `tests/` can substitute for it.

## Verification status (2026-11-09)

| surface | result |
|---|---|
| `pytest -q` on `fix/e019-dogfood` | **38 passed** |
| `python -m tiny_skill_lint examples/` | `no issues`, exit **0** |
| `python -m tiny_skill_lint examples/ --format=json` | `[]`, exit **0** |
| same on `feat/e019-dir-name` (pre-fix) | **E019** on `examples/SKILL.md`, exit **1** |
| CI for PR #3 | **no run queued** (stacked branch) - local result only |
| CI for PR #2 | RED: `test (3.8)` failed on dogfood; 3.9-3.12 `cancelled` |

## Install

```bash
# From GitHub (not on PyPI)
pip install git+https://github.com/hussain-alsaibai/tiny-skill-lint.git
```

Or copy `tiny_skill_lint.py` into your repo and run it directly.

## Usage

```bash
python -m tiny_skill_lint path/to/SKILL.md     # one file
python -m tiny_skill_lint skills/              # directory, recursive
python -m tiny_skill_lint skills/ --format=json   # CI-friendly
python -m tiny_skill_lint skills/ --strict        # warnings become errors
python -m tiny_skill_lint skills/ --config lint.config.json
```

**Exit code is 1 when any record has level `error`, 0 otherwise.** That is
what makes it usable as a CI gate as-is:

```yaml
- name: Lint skills
  run: python -m tiny_skill_lint skills/ --format=json
```

## The 19-Code Catalogue

Verified by importing `ERROR_CODES` on 2026-11-02:

| Code | Level | Description |
|---|---|---|
| E001 | error | Missing required field `name` |
| E002 | error | Missing required field `description` |
| E003 | warn | Description exceeds 800 characters |
| E004 | error | Invalid `name` format (must be kebab-case) |
| E005 | warn | Name is too short (< 3 chars) |
| E006 | error | Invalid `version` (must be semver) |
| E007 | warn | Version is `0.0.0` |
| E008 | error | Unknown required field (frontmatter not a flat-key subset) |
| E009 | warn | Empty `description` |
| E010 | warn | Description contains TODO / FIXME / XXX |
| E011 | warn | Missing `when_to_use` (recommended) |
| E012 | error | YAML parse error |
| E013 | warn | Trailing whitespace in `description` |
| E014 | warn | Name contains uppercase letters |
| E015 | warn | Missing trailing newline |
| E016 | warn | Version is pre-1.0.0 (warn only for libraries in use) |
| E017 | warn | Description first sentence is > 100 chars |
| E018 | error | Invalid `version` semver (E006 supersedes; retained for compat) |
| E019 | error | `name` does not match the parent directory name (agentskills.io spec) |

## E017 Was Unreachable Until 2026-11-02

**The rule could never fire.** `_first_sentence()` capped its own return value
at 100 characters, so the check `len(_first_sentence(desc)) > 100` was
never true. The catalogue listed the code, the docstring described the
behaviour, and the rule had never fired once.

The fix removed the cap, and the reason is now in the docstring so it is not
optimised back in:

```python
def _first_sentence(description):
    """There is deliberately no length cap here. E017 fires when the first
    sentence exceeds the limit, so capping the measurement would make the
    rule unreachable."""
```

**4 regression tests were added; 3 of them fail on the old code.**

See `prompts/a-rule-that-cannot-fire-is-not-a-rule.md` and
`skills/rule-reachability/SKILL.md`.

## The Cross-Compat Claim Was Wrong And Is Gone

Earlier versions of this guide said the linter was *"Cross-compat with
`skillspec/lint` v0.3.0, `skillcheck/core` v0.4.0, and `openskills/lint`
v0.2.0"*. **None of those three names exists on PyPI.** Checked 2026-11-02:

| name | PyPI |
|---|---|
| `skillspec` | **404** |
| `openskills` | **404** |
| `skillcheck` | **200 - but it is a different project** |

`skillcheck` on PyPI is at **v1.5.0**, described as *"Cross-agent skill
quality gate for SKILL.md files conforming to the agentskills.io
specification"*. It is a real package with real usage - a **competitor**, not
a compatibility target. Two of the three names are now taken by unrelated
third-party projects.

**The differentiator is zero dependencies and a CI-gate exit code**, not
catalogue breadth.

## API Surface

```python
from tiny_skill_lint import lint_file, lint_paths, LintRecord, ERROR_CODES
```

`lint_file(path)` and `lint_paths(paths)` return `LintRecord` objects with
`path`, `code`, `level`, and `message` fields.

## Packaging

```toml
requires-python = ">=3.8"
py-modules = ["tiny_skill_lint"]
```

Both verified by reading the upstream `pyproject.toml` on 2026-11-02. The
`py-modules` key is correct here - several sibling packages shipped
`py_modules` instead, which is not a valid key and fails the build.

## Related

- `tools/tiny-skill-md-guide.md` - the parser, validator, renderer, scorer
- `tools/tiny-skill-loader-guide.md` - loading skills at runtime
- `tools/tiny-agentskills-guide.md` - the Agent Skills runtime conventions
