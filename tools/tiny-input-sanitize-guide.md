# tiny-input-sanitize v0.1.0 — Allowlist-First Input Sanitization

**Last verified:** 2026-10-17
**Repo:** https://github.com/hussain-alsaibai/tiny-input-sanitize
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** 398 (lib) + ~600 (tests) • **Tests:** 49/49

## What it solves

When an AI agent or a web service takes a string from outside the trust boundary and feeds it to a shell command, an SQL query, an HTML body, a log file, a filename, or a JSONPath, the question is the same: "is this string safe in *this* context?" The library gives a single, **context-aware**, **allowlist-first** answer with a confidence score instead of a binary pass/fail.

It is **not** a substitute for context-aware output encoding (use `html.escape`, parameterized SQL, `shlex.quote`). It is a fast front-line filter that catches the obvious cases at the boundary so deeply-nested code does not have to.

## Public API

- `sanitize_text(value, *, context="html", allow=None, deny=None, max_length=None, strip_controls=True) -> SanitizationResult`
- `sanitize_for_html(value, **kwargs) -> SanitizationResult`
- `sanitize_for_sql_literal(value, **kwargs) -> SanitizationResult`
- `sanitize_for_shell_arg(value, **kwargs) -> SanitizationResult`
- `sanitize_for_filename(value, **kwargs) -> SanitizationResult`
- `sanitize_for_log(value, **kwargs) -> SanitizationResult`
- `sanitize_for_jsonpath(value, **kwargs) -> SanitizationResult`
- `is_safe(value, *, context="html", threshold=0.95) -> bool`
- `SanitizationResult` dataclass: `value`, `rules_applied`, `confidence`, `truncated`
- `SanitizationContext` enum: `html | sql | shell | filename | log | jsonpath`

## Confidence score (instead of a bool)

- `1.0` — input untouched (no rules matched)
- `0.0` — entire input was removed or replaced
- Otherwise: `1.0 - (transformed_chars / input_length)`

Callers pick their own threshold. `is_safe(value, threshold=0.95)` is a convenience wrapper for the common case.

## Quick start

    from tiny_input_sanitize import (
        sanitize_for_html, sanitize_for_shell_arg,
        sanitize_for_sql_literal, sanitize_for_filename,
        sanitize_for_log, sanitize_for_jsonpath, is_safe,
    )

    # HTML body
    r = sanitize_for_html("<script>alert(1)</script>")
    # r.value == "&lt;script&gt;alert(1)&lt;/script&gt;"
    # r.confidence == 0.0  (the whole input was transformed)
    # r.rules_applied == ["html_chars", "javascript_url"]

    # Shell argument — never build shell strings by hand anyway, but
    # when you must, this is the strip pass.
    r = sanitize_for_shell_arg("hello; rm -rf /")
    # r.value == "hello rm -rf /"  (metachars stripped)

    # Filename
    r = sanitize_for_filename("../../etc/passwd")
    # r.value == "etcpasswd"

    # JSONPath
    r = sanitize_for_jsonpath("$..admin[?(@.secret)]")
    # r.value == "adminsecret"

    # Boolean check at the gate
    if not is_safe(user_input, context="html", threshold=0.95):
        return 400

## Contexts at a glance

| Context | Strips | Notes |
|---------|--------|-------|
| `html` | `< > " ' &`, `javascript:` URLs | escapes, not strips; produces valid HTML |
| `sql` | `' \`` and NUL | escapes; parameterized queries are still required |
| `shell` | `; & | ` $ ( ) > < !` | strips metachars; prefer `shlex.quote` for command building |
| `filename` | `/ \` and reserved names (`CON`, `PRN`, ...) | path traversal blocked; Windows-reserved names blocked |
| `log` | ANSI escapes, NULs, control chars | preserves `\n \r \t` so log lines stay readable |
| `jsonpath` | `$ . [ ] * ? \` and quotes | safe to interpolate as a path component |

## Allowlist-first design

The `allow=` parameter overrides everything: only listed characters survive. `deny=` is for stripping individual characters. They compose — `allow` is applied first, then `deny`. This is the order you want when both are set.

    # Only digits and dashes survive (e.g. UUIDs)
    sanitize_text(s, context="log", allow="0123456789-")

## Pre-processing: NFKC normalization

All inputs go through Unicode NFKC normalization before the per-context transforms. This catches homoglyph attacks (Cyrillic `а` that looks like Latin `a`) at the front door instead of letting them through and relying on downstream string comparison.

## When to use

- Agent tool arguments that are about to be interpolated into shell, SQL, HTML, or filenames
- Web form input that needs a fast front-line filter before deeper validation
- Log lines from external sources before they hit a structured logger
- Filename inputs from users (uploads, exports, downloads)
- JSONPath construction from user input

## When NOT to use

- The string is already trusted (a constant in your codebase)
- You need full HTML sanitization with parser-level understanding of attributes, URLs, CSS — use `bleach` or `nh3` (they have dependencies for a reason)
- You need real shell escaping — use `shlex.quote`
- You need real SQL safety — use parameterized queries
- You need context-aware HTML encoding at render time — use template autoescaping

## Test highlights (49/49)

NFKC normalization + homoglyph detection, allow-vs-deny precedence, six context matrices, max_length truncation + `truncated` flag, control char handling (preserves `\n \r \t` in log context), `is_safe()` threshold behaviour, `SanitizationResult` shape across all six contexts, idempotency on a second pass.
