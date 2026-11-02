---
name: rule-reachability
description: "Prove that every rule in a linter, validator, gate, or checker can actually fire, by constructing an input that triggers each code and asserting it produces that code. Use when adding a rule, when a rule catalogue looks complete but nothing has ever triggered a code, or when a checker reports findings you suspect were never reachable."
---

# Rule Reachability

**Use when:** you add a rule to a linter, validator, gate, or checker; you are
reviewing a rule catalogue; a checker has a code nobody has ever seen fire;
or you are fixing a rule that turns out to be unreachable.

**Do not use when:** the checker is not rule-based (a formatter, a converter, a
report generator). The idea does not apply to code with no catalogue of
outcomes.

**Last verified:** 2026-11-02 - applied to `tiny-skill-lint` (18-code
catalogue, 35 tests passing). Rule `E017` was found to be **unreachable**: the
helper that extracted the first sentence capped its own output at 100
characters, so the rule that fired on `len(sentence) > 100` could never be
true. The fix shipped with 4 regression tests, **3 of which fail on the old
code** and all 4 pass on the new.

## The Core Rule

> **A rule whose precondition is computed by the same code path that evaluates
> it is untested until you try to make it fire.**

A catalogue entry, a docstring, and a test that only checks the checker runs
are all compatible with a rule that has never once fired.

## The Defect

```python
def _first_sentence(description):
    sentence = description.split(".")[0].strip()
    return sentence[:100]        # <- the cap

# the rule that uses it:
if len(_first_sentence(desc)) > 100:      # <- can never be true
    records.append(LintRecord(path, "E017", "warn", ...))
```

The catalogue listed `E017`, the docstring said *"fires when the first
sentence is longer than 100 chars"*, and the rule had never fired once in the
package's life.

The fix removed the cap:

```python
def _first_sentence(description):
    """The measurement is intentionally unbounded. E017 fires when the first
    sentence exceeds the limit, so truncating it here would make the rule
    unreachable."""
```

**The comment matters as much as the code.** The next person to optimise that
helper will otherwise add the cap back, and they will do it for the same
reason it was there in the first place: it looked like a tidy-up.

## Procedure

### 1. Enumerate the catalogue

```python
from tiny_skill_lint import ERROR_CODES
# {'E001': ('error', 'Missing required field `name`'), ...}
```

Every code in this dict needs a fixture.

### 2. Build a fixture per code

A fixture is the smallest input that should produce exactly that code. Keep
them in one place, next to the catalogue:

```python
FIXTURES = {
    "E001": "---\ndescription: no name here\n---\n",
    "E017": "---\nname: x-tool\ndescription: " + "y" * 130 + ".\n---\n",
    ...
}
```

**The fixture must be minimal.** A fixture that trips three rules at once
cannot tell you which one fired.

### 3. Assert each code is reachable

```python
@pytest.mark.parametrize("code", sorted(ERROR_CODES))
def test_each_code_is_reachable(code):
    fixture = FIXTURES.get(code)
    assert fixture is not None, f"no fixture for {code}"
    produced = {r.code for r in lint_text(fixture)}
    assert code in produced, f"{code} did not fire: got {produced}"
```

**A code with no fixture is a decision, not an accident.** If it is genuinely
unreachable, record why in the code:

```python
# E017 previously could not fire: the first-sentence helper capped its own
# output at 100 chars, so len(...) > 100 was never true. Fixed 2026-11-02.
```

### 4. Prove the test is a real test

**Run the new test against the old implementation.** A test that passes on
both the broken and the fixed code is not pinning the fix.

```bash
# revert just the fix, run the new tests, expect failures
git stash push -- <the helper>
python -m pytest -q test_rule_reachability.py   # must FAIL
 git stash pop
python -m pytest -q test_rule_reachability.py   # must PASS
```

In this instance: **3 of the 4 new tests failed on the old code.** All 4 pass
on the new.

### 5. Check the adjacent risk

A helper that computes a rule's input is a **shared** component. When you
find one capped or clamped helper, look for the others:

```bash
grep -n '\[:[0-9]\+\]\|\.truncate(\|\.limit(' <the module>
```

Every slice in a measurement path is a candidate for making a rule
unreachable.

## The Generalisation

This is one instance of a family:

| claim | what it is | how it should be checked |
|---|---|---|
| `requires-python = ">=3.8"` | a promise | run the suite on 3.8 |
| `from fast_cache import cache` | an API | import it |
| rule `E017` fires over 100 chars | a behaviour | construct the input |

> **The claim and the check must be the same thing. A claim with no
> executable check is a comment.**

The test that proves a rule works is not "the checker ran". It is "the rule
fired, and it did not fire before the fix".

## Related

- `prompts/a-rule-that-cannot-fire-is-not-a-rule.md`
- `prompts/mutation-test-proves-the-test.md` - inject the defect, confirm the
  suite catches it
- `prompts/zero-tests-ran-is-a-failure.md` - a suite that collects nothing
  reports green
- `prompts/python-support-is-a-claim.md` - a declared support claim nobody
  tested
- `prompts/readme-claims-must-be-runnable.md` - a documented API that does not
  exist
