# Probing a Boundary in Five Lines

**Last verified: 2026-11-24** — the probe below found the `tiny-log` 0.8.3 unit
bug in under a minute on a tree whose 140-test suite was green, and confirmed
the `tiny-validator` 0.7.4 nullable fix before any test was written.

## The rule

**Before writing a test, before reading the diff, run the function at the
boundary in a REPL.** One line per boundary input.

```python
import tiny_log as t
for v in (1023.9999, 1048575.99, 0, -1, float("nan"), float("inf")):
    print(v, "->", t.bytes_human(v))
```

Output on the broken release:

```
1023.9999     -> 1024.0 B      # number equals the next unit's base; label says B
1048575.99    -> 1024.0 KB
0             -> 0 B
-1            -> -1 B
nan           -> NaN B
inf           -> OverflowError # raised INSIDE a logging call
```

Out of one probe: a 1024x error, a contradiction between value and unit, and an
exception from a formatter that must never raise.

## Which inputs to try, in this order

1. **Just below a change boundary** — `1024 - ε`, `99 - ε` for a two-digit
   format, `rate * 0.999`. This is where "computed separately" bugs live.
2. **The sentinels** — `0`, `-0.0`, `None`, `""`, `inf`, `-inf`, `NaN`.
3. **The empty and the one-element collection** — `[]`, `[None]`.
4. **The round trip** — `parse(render(x)) == x`, `import(export(s))` valid.
5. **The type variants** — `True` (an int), `1` vs `"1"`, enum vs its name
   (`logging.DEBUG` → `"10"` → lookup by `"DEBUG"` fails).

## Why five lines beat a suite rerun

The suite proves the cases it names. The probe names the case the suite cannot
guess — the one where two halves of the same fact disagree. It costs seconds,
and it produces a **receipt** (the before/after output) that goes straight into
the commit message.

## Anti-patterns

- Probing after the fix, to "confirm" — that confirms nothing; run it on the
  broken tag first and keep the output.
- Probing with a sample from the middle of the domain (`1536`, `2.5 MB`) —
  every one of those passes on the broken code.
- Trusting a green suite as evidence the boundary is covered. Grep the tests
  for the literal boundary value; if it is absent, it is not covered.
