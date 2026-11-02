# A Rule That Cannot Fire Is Not A Rule

**A rule for any linter, validator, gate, or checker with a rule catalogue.**

> Found 2026-11-02. The rule `E017` — *"description first sentence is longer
> than 100 characters"* — **could never fire.** The helper that extracted the
> first sentence capped its own return value at 100 characters, so the length
> it measured was never greater than the threshold it was comparing against.
> **Last verified:** 2026-11-02 — the fix was confirmed by 4 regression tests
> that **fail 3 of them on the old code** and pass on the new.

## The Rule

> **If a rule's precondition is computed by the same code path that evaluates
> it, the rule is untested until you try to make it fire.** A rule catalogue
> that lists a code nobody has ever triggered is a catalogue of intentions.

## The Defect

```python
def _first_sentence(description):
    sentence = description.split(".")[0].strip()
    return sentence[:100]        # <- the cap

# ... and then the rule that uses it:
if len(_first_sentence(desc)) > 100:      # <- can never be true
    records.append(LintRecord(path, "E017", "warn", ...))
```

The rule's own docstring said *"fires when the first sentence is longer than
100 chars"*. The implementation made that impossible. **The catalogue listed
the rule, the docs described the rule, and the rule had never fired once.**

The fix removed the cap:

```python
def _first_sentence(description):
    """Return the first sentence (text up to . ! ?, else the whole string).

    There is deliberately no length cap here. E017 fires when the first
    sentence is *longer* than 100 chars, so truncating to 100 inside this
    helper made the rule unreachable -- any description without sentence
    punctuation produced exactly 100 chars and never triggered E017.
    """
    for i, c in enumerate(description):
        if c in ".!?" and i > 0:
            return description[: i + 1]
    return description
```

## The Test That Proves It

A rule's test must **assert that the rule fires**, not only that the checker
runs. The regression test that matters is written so that it fails against
the old implementation:

```python
def test_e017_fires_on_long_first_sentence():
    # 130-char first sentence. Under the old cap this was truncated to 100
    # and the rule could not fire.
    desc = "x" * 130 + ". Second sentence is fine."
    records = lint_file(path_with_description(desc))
    assert any(r.code == "E017" for r in records)
```

**Verification that it is a real test:** run it against the old code and
confirm it fails. A test that passes on both the broken and the fixed
implementation is not pinning the fix. In this case **3 of the 4 new tests
failed on the old code** and all 4 pass on the new.

## The Sweep

The general form: **for every rule in the catalogue, construct an input that
should trigger it, and assert it does.**

```python
# For each rule code in the catalogue, there must be at least one case that
# produces exactly that code.
@pytest.mark.parametrize("code", sorted(CATALOGUE))
def test_each_code_is_reachable(code):
    fixture = FIXTURES.get(code)
    assert fixture is not None, f"no fixture for {code}"
    assert code in codes_produced_by(fixture)
```

A code in the catalogue with no fixture is a rule nobody has ever seen fire.
That is not automatically a defect — it may be genuinely unreachable — but it
**must be a decision, not an accident.** Record it:

```python
# E017 previously could not fire: the first-sentence helper capped its own
# output at 100 chars, so len(...) > 100 was never true. Fixed 2026-11-02.
```

## Why This Belongs To A Bigger Pattern

This is the same defect shape as `prompts/python-support-is-a-claim.md` (a
declared support claim nobody tested) and
`prompts/readme-claims-must-be-runnable.md` (a documented API that does not
exist). In all three, **a description exists, and the description is not
connected to the code.**

| claim | what it is | how it was supposed to be checked |
|---|---|---|
| `requires-python = ">=3.8"` | a promise | run the suite on 3.8 |
| `from fast_cache import cache` | an API | import it |
| rule `E017` fires over 100 chars | a behaviour | construct the input |

**The rule that covers all three: the claim and the check must be the same
thing.** A claim with no executable check is a comment.

See also `prompts/mutation-test-proves-the-test.md` (inject the defect and
confirm the suite catches it) and `prompts/zero-tests-ran-is-a-failure.md` (a
suite that collects nothing reports green).
