# A new lint rule must pass on the repo's own fixture before the branch is called done

**First recorded:** 2026-11-09
**Last verified:** 2026-11-09 — fresh clone of `tiny-skill-lint` branch
`fix/e019-dogfood` (`d2e70d9`): `pytest -q` → **38 passed**,
`python -m tiny_skill_lint examples/` → `no issues` (exit 0), `--format=json`
→ `[]` (exit 0). The un-fixed branch reproduces the E019 error on
`examples/SKILL.md`, exit 1.

> **Merge notice:** this prompt overlaps
> `prompts/a-lint-rule-must-be-proven-to-reject.md`, which covers the same
> incident from the rule-design side (rejection test / dogfood / negative
> control). Read that one for the three-part taxonomy. This file keeps only the
> operational rule and the CI mechanics; merge or delete on review.

## The operational rule

Before pushing any new lint rule, a linter, validator or schema check:

```bash
python -m <linter> examples/        # or fixtures/ , tests/data/
```

Exit 0, or the fixture is wrong. It takes a second and it is the only step that
exercises a **real** file on disk rather than one built inside a test.

## Why unit tests do not cover this

| proof | question it answers | question it leaves open |
|---|---|---|
| happy-path tests | does normal input still pass? | does the new rule reject anything? |
| rejection test | does the rule fire on a violation? | does it fire on something **valid**? |
| mutation / stub test | is the rule load-bearing? | is the rule **satisfiable** at all? |

The E019 branch had all of the first three and still shipped a rule that
rejected the repository's own example.

## The CI mechanics that hid it

PR #2's checks on 2026-11-08:

| job | conclusion |
|---|---|
| `test (3.8)` | **failure** (dogfood step) |
| `test (3.9)`–`test (3.12)` | `cancelled` |

That is not "one flaky failure". Fail-fast cancelled the other four, so
**four Python versions were never tested**. A matrix must be reported by
per-job conclusion, never by the run's overall verdict — the same defect class
as `prompts/a-green-badge-can-hide-a-failed-job.md`, in the opposite
direction.

## Applied fix

`examples/SKILL.md` → `examples/skill-authoring/SKILL.md`: the directory shape
the spec requires and the shape every real bundle has. Dogfood step, README
and CHANGELOG repointed; CHANGELOG entry records the root cause. PR #3 is
stacked on `feat/e019-dir-name` and GitHub queued **no workflow run** for it,
so the verification is local and is labelled local.

## Related

- `prompts/a-lint-rule-must-be-proven-to-reject.md` (same incident, taxonomy)
- `prompts/zero-tests-ran-is-a-failure.md`
- `prompts/a-guard-that-fails-open-passes-every-happy-path-test.md`
- `skills/rule-reachability/SKILL.md`
