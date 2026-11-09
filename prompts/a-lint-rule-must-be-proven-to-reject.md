# A Lint Rule Must Be Proven to Reject — and Proven Not to Be Vacuous

**A rule for shipping any new check, linter rule, or validator condition.**

> Found 2026-11-08 while adding E019 ("`name` must match the parent directory
> name", from the agentskills.io spec) to `tiny-skill-lint`. The rule was
> correct, the unit tests were green, and the repository's **own bundled
> example failed it**. **Last verified:** 2026-11-09 — every measurement below
> was re-run on a fresh clone of `feat/e019-dir-name` (`36/38 tests`) with
> `python -m tiny_skill_lint` against prepared fixture trees.

## The failure mode, in three parts

A new rule can be wrong in three independent ways, and a green test file
usually only rules out the first.

| # | What can be wrong | What catches it |
|---|---|---|
| 1 | The rule does not fire when it should | a **rejection** test |
| 2 | The rule fires on things that are valid | the repo's **own fixtures** / dogfood step |
| 3 | The rule's acceptance says nothing | a **negative control**: an input that is invalid on every *other* axis but passes this rule |

The 2026-11-08 run hit (1) and (2). The 2026-11-09 run hit (3), which no
amount of the first two would have found.

## Part 1 — a rejection test

```python
def test_name_must_match_parent_dir(tmp_path):
    d = tmp_path / "api-dev"; d.mkdir()
    (d / "SKILL.md").write_text(valid_skill(name="other-name"))
    codes = [r.code for r in lint_file(d / "SKILL.md")]
    assert "E019" in codes
```

Written this way the test proves the rule exists. It does not prove the rule
can be *satisfied* by something valid, and it never touches a real skill tree.

## Part 2 — the repo's own fixtures are the cheapest dogfood

E019 shipped with `examples/SKILL.md` declaring `name: skill-authoring`. The
rule requires the parent directory to equal the name, so the example — a file
sitting directly in `examples/` — was **unlintable by construction**. CI's
dogfood step (which lints `examples/` to prove the linter works) went red on
Python 3.8 and reported the other four matrix jobs as `cancelled`.

```
E019 error  'name' (skill-authoring) does not match parent directory (examples)
```

The fix is structural, not a suppression: the fixture becomes a real bundle,
`examples/skill-authoring/SKILL.md`, which is the shape a skill actually
ships in.

> **A rule that cannot pass on the repository's own example has not been
> deployed yet, whatever the test count says.**

Secondary lesson: a matrix where one job fails and the rest are `cancelled`
reads like "one flaky failure". It is really "four versions untested".

## Part 3 — the negative control, which is where the rule broke

E019 passes when `parent_dir == name`. Nothing else. So a name that is
invalid on every *other* axis passes E019 **iff** the directory is spelled the
same way. Measured on the published branch:

| fixture | name | dir | findings |
|---|---|---|---|
| `mut5/--/SKILL.md` | `--` | `--` | **E005 warn** (`< 3 chars`) — **exit 0** |
| `mut6/1abc/SKILL.md` | `1abc` | `1abc` | E004 error (kebab-case) |
| `mut4/a b/SKILL.md` | `a b` | `a b` | E004 error |
| `mut3/Some_Dir../SKILL.md` | `Some_Dir..` | `Some_Dir..` | E014 warn (uppercase) — **exit 0** |

```
$ python -m tiny_skill_lint /tmp/mut5 --format json
[{"code": "E005", "level": "warn", "message": "Name is too short (< 3 chars)"}]
$ echo $?
0
```

`--` is not a skill name under any reading of the spec: it starts with a
hyphen and has no alphanumeric character at all. It exits 0.

**The cause is the rule that was already there.** `_check_kebab()` begins
`if not name or len(name) < 3: return False`, and `lint_file` then suppresses
E004 whenever `short` is true:

```python
if not kebab_ok and not short and not upper:
    records.append(... "E004" ...)
```

So for any name shorter than three characters, **the kebab-case rule is
unreachable and E019 is the only name rule left** — and E019 is satisfied by
copying the bad name into the directory name. Two defects, one shipped rule:
an early `return` inside a predicate that turns a real check into silence, and
a new rule whose only positive case is trivially reachable.

`--` should be an **error**, not a warning: the spec's naming rule is a
requirement, not a style hint, and `_check_kebab` already computes the right
answer — the caller throws it away.

## The checklist

1. **Rejection** — write the test that fires the rule.
2. **Dogfood** — run the linter over the repo's own `examples/` and its own
   skill trees before the branch is called done. One second:
   `python -m tiny_skill_lint examples/`.
3. **Negative control** — construct an input that fails *every other* rule
   and assert this rule still fails it. If that input passes, the rule is
   satisfiable by garbage.
4. **Reachability** — for each new rule, `grep` the predicate it depends on
   and ask whether an earlier guard has already returned. A `return False` in
   the middle of a validator is the most expensive line in the file.
5. **Severity** — if a rule encodes a requirement, `error`. A warning whose
   exit code is 0 is a suggestion that CI cannot act on.

## Where this lives

- `hussain-alsaibai/tiny-skill-lint` — the E019 fixture fix is PR #3 (base
  `feat/e019-dir-name`); the `--` / short-name reachability defect is recorded
  here as a measurement and **not yet fixed upstream**.
- Workspace side: 35 findings across the local `skills/` tree
  (`E012` 16, `E011` 8, `E006` 7, `E008` 3, `E019` 1) — a backlog, and one
  `E019` that is a real path/name mismatch (`codebuddy-code` ships
  `name: codebuddy-cli`).
