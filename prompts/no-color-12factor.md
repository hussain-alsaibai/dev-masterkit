# no-color-12factor — Prompt for 12-Factor ANSI Color Decisions

## Description

Steers an agent implementing TTY-aware color output to respect `NO_COLOR`
(https://no-color.org) and to provide a documented override. Prevents the
common bug where `sys.stdout.isatty()` returns `False` under pytest, IDE test
runners, and cron — making color "just disappear" in CI.

## The Prompt

```
You're adding ANSI color output to a CLI or logger. Make the decision
explicit and 12-factor compliant.

Checklist:

1. **Detect TTY correctly.** Use `sys.stdout.isatty()`. Be aware this returns
   False under:
     - pytest (unless `-s` is passed)
     - VS Code / PyCharm test runners
     - cron and systemd timers
     - any captured stdout (`contextlib.redirect_stdout`)
2. **Honor `NO_COLOR`.** Per https://no-color.org, ANY non-empty value of
   the `NO_COLOR` environment variable disables color, regardless of TTY.
     ```python
     def _wants_color() -> bool:
         if os.environ.get("NO_COLOR"):
             return False
         return sys.stdout.isatty()
     ```
3. **Provide a force override.** Add a project-specific env var for tests
   and CI debugging:
     ```python
     force = os.environ.get("MYAPP_FORCE_COLOR")  # not "MYAPP_FORCE_COLOR=1" — any value
     if force or os.environ.get("FORCE_COLOR"):
         return True
     ```
4. **Respect precedence.** Override > NO_COLOR > TTY. Order of checks:
     force ON → NO_COLOR → TTY → default OFF
5. **Test all four modes.** A unittest that mocks `os.environ` and
   `sys.stdout.isatty()` to verify each branch.

Reporting:
- Document the precedence order in a "Color" section of the README.
- Add the env vars to a "Configuration" table.
- Note any ANSI codes that don't degrade gracefully on Windows legacy
  console (use `colorama`-style fallbacks only if targeting Windows).

Common pitfall: a test that sets `os.environ["MYAPP_FORCE_COLOR"] = "1"`
but checks truthiness via `os.environ.get(...) is None`. Use truthiness,
not identity.
```

## When to Use

- Any CLI tool that emits ANSI escape codes
- Loggers with color-coded severity levels
- Linters, formatters, and diff renderers

## Last Verified: 2026-06-30