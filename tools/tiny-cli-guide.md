# tiny-cli — Zero-Dependency CLI Builder

## Repo
https://github.com/hussain-alsaibai/tiny-cli

## One-liner
Click-style CLI builder with `@app.command()`, `@option`, `@argument`.
ANSI color with TTY auto-detect, NO_COLOR compliant. ~250 LOC.

## Install
```bash
pip install tiny-cli
```

## Quick Example
```python
from tiny_cli import App

app = App(name="greeter", help="Say hi to people")

@app.command("greet")
@option("--name", required=True, help="Who to greet")
@option("--shout", type=bool, help="SHOUT the greeting")
def greet(name: str, shout: bool = False) -> None:
    msg = f"Hello, {name}!"
    if shout:
        msg = msg.upper()
    print(app.color(msg, "green"))

if __name__ == "__main__":
    app.run()
```

## Color / TTY Rules
- `sys.stdout.isatty()` controls default color
- `NO_COLOR=anything` disables color (https://no-color.org)
- `TINY_CLI_FORCE_COLOR=1` forces color on (use in tests / CI debugging)
- `TINY_CLI_FORCE_COLOR=0` forces color off (overrides TTY)

## The Boolean-Flag Trap
For boolean flags, use `type=bool` in your decorator — the wrapper detects
this and uses `argparse`'s `action="store_true"` automatically.

```python
# ❌ WRONG — argparse expects a value for `--shout`
@option("--shout", type=bool)
def greet(name, shout): ...

# ✅ RIGHT — tiny-cli detects type=bool and uses store_true internally
@option("--shout", type=bool)  # this works correctly in tiny-cli
def greet(name, shout=False): ...
```

If you're rolling your own wrapper and `--shout Alice` errors with
"expected one argument", you forgot `action="store_true"`. Fix in
`App._build_parser`:

```python
kwargs = {"action": "store_true"} if m["type"] is bool else {"type": m["type"]}
parser.add_argument(m["name"], **kwargs)
```

## Prompt / Confirm
```python
name = app.prompt("Your name? ")
if app.confirm("Continue?", default=True):
    ...
```

## Benchmarks
- Color wrap: 258 ns per call
- Argument parse: ~80 µs for a 5-option command

## Tests
13/13 passing.

## Last Verified: 2026-06-30