# A raw string cannot escape its own quote

**Last verified:** 2026-11-13 (12:00 EST) — `ai-git-hooks` `_parse_response`
raised `SyntaxError` on import; repaired and proved by behaviour. 9 of 22 tests
failed with the broken pattern restored, 22 passed with it correct.

## The rule

> **An `r'...'` literal has no escape hatch for `'`.** If the pattern contains
> the delimiter, change the delimiter (`r"..."`) or build the string in pieces.
> Never `r\'...\'` — in a raw string the backslash does not escape, so the
> quote **closes** the literal.

## What it looked like

```python
match = re.match(r\'\[(\w+)\]\s*(\w+):\s*(.+)\'', line)   # SyntaxError
```

`ruff` reported it as 10 cascading `invalid-syntax` errors across lines 41-59.
That reads like a broken *file*; it was one broken *literal*.

## The second bug the syntax was hiding

The first repair produced:

```python
re.match(r'\[\(w+)\]...', line)     # parses, matches nothing
```

The group `(\w+)` had lost its backslash and become a literal `(`. Every
`[HIGH] security: ...` finding silently fell through the unstructured branch
and was recorded as `severity=info, category=general`. The module went from
*cannot import* to *imports and quietly mislabels everything* — worse.

**A repair is proven by behaviour, not by the absence of an error.**
`ast.parse()` passing is necessary and nowhere near sufficient:

```python
assert _parse_response('[HIGH] security: SQL injection in login') == (
    'HIGH', 'security', 'SQL injection in login')
```

## Checklist

1. Delimiter differs from any quote in the pattern.
2. `python -c "import module"` — not just the linter.
3. One known-input assertion per regex on a string that *does* match.
4. Restore the broken pattern and confirm the tests go red.
