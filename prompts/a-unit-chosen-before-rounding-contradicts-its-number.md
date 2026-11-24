# A Unit Chosen Before Rounding Contradicts Its Own Number

**Last verified: 2026-11-24** — `tiny-log` 0.8.3 (`04c74a1`). Unit promotion
verified on `bytes_human(1023.9999)` → `"1 KB"`, `bytes_human(1048575.99)` →
`"1 MB"`, `bytes_human(1023.6, precision=0)` → `"1 KB"`, `bytes_human(inf)` →
`"inf B"`. 13 tests added, 8 red on 0.8.2, suite 140 passed / 16 skipped.

## The problem

A formatter that picks a unit **first** and rounds **second** produces a
number that its own suffix denies — but only inside one rounding step of a
base boundary:

```python
bytes_human(1023.9999)   # "1024.0 B"
```

`1024.0 B` is 1024 bytes' worth of digits labelled with the byte unit. Any
caller that strips the suffix and parses the number — which is exactly what a
dashboard does with a telemetry field — reads a **1024x** error. The value is
never wrong by more than one rounding step, so a test that samples anywhere
except the boundary passes.

## Why the suite did not catch it

Every existing test sampled the *centre* of an input domain: `512`, `1536`,
`1572864`. Rounding code is only wrong at the boundary and at the sentinel
(`0`, `±inf`, `NaN`), and none of those were named by a test.

**A green suite proves the cases it names.** For anything that rounds, promotes
units, or has a sentinel input, add a test *at* the boundary, not near it.

## The fix

Promote **after** rounding, and compare the **rounded value**, not the rendered
string (string comparison makes formatting part of the condition):

```python
eff_precision = max(0, precision if precision is not None else 1)
rendered = _render_magnitude(value, eff_precision)
while idx < len(units) - 1 and round(value, eff_precision) >= 1024:
    value /= 1024.0
    idx += 1
    rendered = _render_magnitude(value, eff_precision)
```

Three sibling defects were in the same function, and all three are the same
shape — **a guard that covered one of two symmetric cases**:

| input | bug | fix |
|---|---|---|
| `precision=0` | `int(v)` truncates where `f"{v:.0f}"` rounds | `int(raw + 0.5)` at precision 0 |
| `float("inf")` | `int(value)` raises `OverflowError` **inside a logging call** | explicit `±inf` guard beside the existing NaN guard |
| `SamplingHandler(rates={logging.DEBUG: 0.0})` | key stored as `"10"`, looked up as `"DEBUG"` → rate read back as default `1.0`, **every** record kept | normalise int levels via `logging.getLevelName` |

## The probe that found it

A five-line REPL call — one line per boundary — found the unit bug in under a
minute while the 140-test suite was already green:

```python
for v in (1023.9999, 1048575.99, 0, float("inf")):
    print(v, bytes_human(v))
```

Run the probe **before** writing the test and before reading the diff. It is
cheaper than any rerun, and it names the failing boundary directly.

## Related

- `prompts/two-computed-separately-things-must-agree.md` — the agreement
  invariant this defect violates (value vs. unit).
- `tools/probing-a-boundary-in-five-lines.md` — the procedure.
