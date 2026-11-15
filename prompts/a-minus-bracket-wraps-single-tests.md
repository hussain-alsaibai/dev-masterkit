---
name: a-minus-bracket-wraps-single-tests.md
description: Use when running a pytest `-k` filter — `-k` takes a boolean expression and the space-separated form is implicit AND, not a list; `-k not (a or b)` is required to exclude two things.
---

# `-k` is an expression, and a `-k` that excludes two things negates a bracket

## The prompt

> Write every `-k` as if it will be evaluated. `-k x y` is not two filters.

## What happened

Excluding two directories from a pytest run, this is the intuitive form and it
is wrong:

```bash
pytest -k "not test_cli and not test_schema"    # correct: two terms
pytest -k "not slice and not long"               # correct
```

The form people reach for — a single `not` in front of a list — does not
exist:

```bash
pytest -k "(not slice, not long)"      # SyntaxError in the -k expression
pytest -k "not slice long"             # parses as not(slice AND long) — excludes almost nothing
```

`-k` evaluates a Python boolean expression over the test **id**. Adjacent
tokens are implicit `and`. A leading `not` binds to the whole remaining term, so
`not a b` means `not (a and b)`, which selects nearly everything. Excluding two
independent substrings requires either two `not` terms joined by `and`, or one
parenthesised `or` under one `not`:

```bash
pytest -k "not (slice or long)"
```

## Why this one is worth a file

The failure is **silent and green**. `-k "not slice long"` runs, exits 0, and
runs more tests than intended — never fewer. A run that collected more than
expected looks like a passing run, and the excluded modules are exactly the ones
you excluded because they were slow or environment-dependent. The evidence is
in the collected count (`-k` prints `N/M tests collected`), which is the line
everyone skips.

## The rule

1. **Read the collected count, not the exit code.** `deselected` present and
   equal to your intended count is the check. `pytest -q -k "..." --co`
   lists exactly what is in scope without running anything.
2. **Prefer the filesystem to the expression.** If a directory should be
   excluded, pass explicit paths (`pytest tests/unit`) or add it to
   `norecursedirs`. `-k` filters by id substring and will match a name you did
   not anticipate — including the same word inside a *test class's* path.
3. **`--doctest-modules` collects docstrings as tests.** That is usually why a
   filter is needed at all; excluding by directory is more durable than by
   name, because a docstring example does not have a name you can predict.

## How to verify

```bash
pytest -q -k "not (slice or long)" --co | tail -1   # the number that matters
pytest -q -k "not slice long" --co | tail -1        # and compare: this one is larger
```

If the two counts agree, the expression was already equivalent.

---

**Last verified:** 2026-11-15 — session note recorded the `-k "(not slice, not
long)"` attempt and the reason for the actual form; the count-comparison check
above is the discriminator. Only the correct form was used in the runs cited in
`daily-updates/2026-11-15.md`; the malformed forms are documented here so they
are not tried again.
