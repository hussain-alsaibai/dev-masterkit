# yaml-debug-tuple-unpack — Prompt for Debugging Subset YAML Parsers

## Description

Debugs a common bug in hand-rolled subset YAML parsers where `_yaml_parse_block`
returns a `(value, position)` tuple but callers use `isinstance(parsed, dict)`,
which is always `False` on a tuple. Steers the agent toward the canonical fix:
unpack the tuple.

## The Prompt

```
You're debugging a Python utility with a hand-rolled YAML subset parser.
`_yaml_parse_block(text, pos)` returns `(value, end_pos)` but every caller
crashes with `ValueError: ... expected dict, got tuple`.

Walk through this systematically:

1. **Find the contract.** Read `_yaml_parse_block` and confirm the return shape.
   Is it a tuple `(value, position)` or just the value?
2. **Find every caller.** `grep -rn '_yaml_parse_block' .` and inspect each.
3. **Classify the failure mode.** `isinstance(tuple, dict)` is always `False`,
   so any `if isinstance(parsed, dict): ... else: raise ValueError(...)` will
   always raise. Confirm via a one-liner:
     ```python
     parsed = _yaml_parse_block("a: 1", 0)
     print(type(parsed), parsed)
     ```
4. **Apply the fix.** Replace `parsed = _yaml_parse_block(...)` with
   `parsed, _ = _yaml_parse_block(...)` at every caller. The trailing `_`
   signals that the position is intentionally discarded (we know the parser
   advanced past the block).
5. **Add a regression test.** A minimal YAML snippet that previously raised
   should now return a dict.

Reporting:
- How many call sites needed fixing?
- Any caller that legitimately needed `end_pos`? If so, name it and keep the
  unpack.
- Confirm the test suite still passes.

Rule: never patch the parser to return a non-tuple just to satisfy broken
callers — fix the callers. The tuple contract is correct.
```

## When to Use

- Hand-rolled parsers (YAML subset, TOML subset, INI subset, etc.) returning
  `(value, position)`
- Tests passing individually but failing when chained
- `ValueError: expected dict, got tuple` style errors

## Last Verified: 2026-06-30