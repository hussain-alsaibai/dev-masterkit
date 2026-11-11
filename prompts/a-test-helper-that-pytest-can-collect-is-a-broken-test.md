# A test helper that pytest can collect is a broken test

**Discovered:** 2026-11-11 (snapdb 0.18.0, fixed in 0.18.1 `55cc77f`)
**Last verified:** 2026-11-11 — unpacked sdist of 0.18.0 → **2 failed + 2
errors**; same tree with the helpers renamed → 0 errors

## The bug

Two test modules in `snapdb` defined a helper at module level:

```python
def test(name, ok, detail=""):
    ...   # asserts `ok`, prints `detail`
```

39 call sites used it as `test("version", a == b)`. That is a perfectly ordinary
way to write a table-driven test — except `pytest` collects any module-level
function whose name starts with `test`, treats its parameters as **fixtures**,
and fails the module with:

```
fixture 'name' not found
```

It errored on **every** run, including the author's, because the function is
collected wherever the file is imported.

## Why it survived

The file also ran fine under a bare `python tests/test_delta_encoding.py`
invocation, where `test(...)` is just a call. Two entry points to the same file,
one of which works, and the working one is the one people run by hand.

The correct fix is the smallest one: rename the helper to `check()`. Do not add
a `__test__ = False` marker, and do not add `test` to `python_functions` —
both hide a live landmine rather than remove it.

## The general rule

`pytest` claims the namespace by prefix. Anything at module level starting with
`test` is not yours: not a helper, not a factory, not a decorator, not a
dataclass. The same applies to `Test*` classes, which pytest also collects and
will try to instantiate.

`conftest.py` is the escape hatch that stays true: helpers there are imported,
not collected.

## Detection

Collected-count comparison catches this class without knowing the name of the
bug — `pytest --collect-only -q` reports what pytest believes exists:

```bash
pytest --collect-only -q | tail -1     # e.g. "412 tests collected"
grep -rc '^def test' tests/            # the number you expected
```

A module erroring at collection shows up as `errors` in the summary line even
when every other file is green, which is why the sdist run in
`prompts/a-test-that-only-runs-in-a-checkout-is-a-test-that-never-ran.md` found
this one: the tarball run surfaced both defects, and the checkout surfaced
neither.
