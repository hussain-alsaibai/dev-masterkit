# cli-bool-flag-pattern — Prompt for Correct argparse Boolean Flags

## Description

Steers the agent to use `action="store_true"` (not `type=bool`) for boolean CLI
flags when wrapping or hand-rolling argparse. Without it, `--shout` triggers
"expected one argument" because argparse tries to consume the next argv item.

## The Prompt

```
You're building a Python CLI and the boolean flags don't work.
Reproducer: `python my_cli.py greet --shout Alice` fails with
`error: argument --shout: expected one argument`.

Diagnose and fix:

1. **Confirm the wrapper layer.** If you have a `@option` decorator that
   inspects a dict like `m = {"name": "--shout", "type": bool}`, the wrapper
   is the most likely culprit. Look at how it calls `parser.add_argument`.
2. **Why `type=bool` fails.** argparse evaluates `bool` at parse time and then
   expects a value string to convert. `--shout Alice` makes argparse think
   "Alice" is the bool value. There is no bool converter registered, so it
   errors out before consuming `--shout` as a flag.
3. **Apply the canonical fix.** In your wrapper, detect bool options and use
   `action="store_true"`:
     ```python
     kwargs = {"action": "store_true"} if m["type"] is bool else {"type": m["type"]}
     parser.add_argument(m["name"], **kwargs)
     ```
4. **Add a test.** A test that invokes the CLI with `--shout` (no value)
   and asserts the option is `True`.
5. **Negative case.** Test `--shout false` is NOT a valid form — argparse
   store_true has no way to express "explicitly false". Document this in the
   README: "boolean flags default to False; presence sets them True."

Bonus: also check `default=False` is set explicitly so the option is always
defined regardless of whether the flag was passed.

Reporting:
- Show the failing command and the new passing command.
- Note the line(s) changed in the wrapper.
```

## When to Use

- Hand-rolled argparse wrappers (Click-style decorators, tiny-cli style)
- `--verbose`, `--debug`, `--quiet`, `--shout`-style boolean flags
- "expected one argument" errors on flag-style options

## Last Verified: 2026-06-30