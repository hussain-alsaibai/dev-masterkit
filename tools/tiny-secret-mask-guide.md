# tiny-secret-mask v0.5.1 — When Security Code Fails Silently

> Zero-dependency secret redaction for logs, HTTP responses, and JSON.
> v0.5.1 is a **correctness release**: the v0.4.0/v0.5.0 sidecars were not
> packaged, so `mask_route_path()` and `mask_headers()` degraded to **identity
> functions that looked like they worked**. Route and header redaction were
> silently doing nothing in any install.
> Last verified: 2026-10-21 | Version 0.5.1 | hussain-alsaibai/tiny-secret-mask

## The Defect

`pyproject.toml` declared only two modules:

```toml
py-modules = ["tiny_secret_mask", "tiny_secret_mask_v020"]
```

but the v0.4.0 and v0.5.0 sidecars existed on disk and were never listed.
The top-level module imported them inside `try/except ImportError` and fell
back to **identity lambdas**:

```python
except ImportError:  # pragma: no cover - single-file fallback
    _V040_AVAILABLE = False
    mask_route_path = lambda path, redactor=None: path   # <- identity, silently
```

Result: `mask_route_path("/u/550e8400-...")` returned the UUID unchanged.
The calling code was correct. The guarantee was not. **No exception, no log
line, no metric** — a security control that reported success while doing
nothing.

## The Five Fixes

| # | Fix | Class |
|---|-----|-------|
| 1 | Add `_v040`, `_v050` to `py-modules` | packaging |
| 2 | Fallback raises `RuntimeWarning` naming the broken guarantee | observability |
| 3 | `base64url_20` moved LAST in `PATH_REDACT_RULES` + tightened | correctness |
| 4 | `safe_repr` depth semantics split primitive vs container | correctness |
| 5 | 6 catalogue patterns shipped examples matching nothing | test integrity |

### 1-2. Never let a security function degrade to a no-op

The general rule this release encodes: **a redaction function that cannot
redact must fail loudly.** Fixed now with a warning that names the guarantee
and the repair:

```python
warnings.warn(
    "tiny-secret-mask: route-path redaction is UNAVAILABLE "
    "(tiny_secret_mask_v040 not importable: %s). mask_route_path() is an "
    "IDENTITY function - secrets in URLs will NOT be redacted. Fix: ...",
    RuntimeWarning, stacklevel=2,
)
```

### 3. Rule order is part of the rule

`PATH_REDACT_RULES` is an ordered list, and `RoutePathRedactor.apply()` walks
it in order. `base64url_20` sat **4th**, ahead of `aws_access_key`,
`github_pat`, `jwt_fragment`, `slack_token`, `stripe_live`, `openai_key`,
and `google_api_key`. Every one of those was already masked by the time its
own rule ran:

```
/keys/AKIAIOSFODNN7EXAMPLE/active   ->  /keys/[REDACTED:base64url_20]/active   # WRONG
/keys/AKIAIOSFODNN7EXAMPLE/active   ->  /keys/[REDACTED:aws_access_key]/active # RIGHT
```

The secret was still hidden, so this never looked like a failure — but the
operator could not tell *what* leaked, which rule to tune, or which severity
it was. The fix is two-part: move the single catch-all rule to the **end** of
the catalogue, and tighten it so it requires a digit, a letter, and one of
`_-/` so ordinary URL segments are not redacted wholesale.

**Rule for any ordered pattern catalogue: exactly one catch-all, always last,
and a test that asserts each rule fires *by name* on its own example.**

### 4-5. Tests that pin versions and placeholder examples

- `safe_repr(obj, depth=0)` returned `""` for containers, so truncation was
  invisible. Now primitives at exhausted depth render `""` and containers
  render the `[...]` prune marker.
- 6 `PATTERN_CATALOG` entries shipped elided examples (`"e3b0c44..."`,
  `"***..."`) that matched no regex. Replaced with concrete generated
  strings.
- `bearer` was case-sensitive, so its own documented example
  `Authorization: Bearer ***` never matched. Added `(?i)`.
- Three version tests pinned the package at 0.1.0 / 0.2.0 / 0.4.0 forever.
  Now they assert the sidecar version and that the package is `>=` it.

## Verified Behaviour

```
mask_route_path("/u/550e8400-e29b-41d4-a716-446655440000")  ->  /u/[REDACTED:uuid]
mask_route_path("/keys/AKIAIOSFODNN7EXAMPLE/active")         ->  /keys/[REDACTED:aws_access_key]/active
mask_route_path("/ghp_" + "a"*36)                            ->  /[REDACTED:github_pat]
mask_route_path("/api/v1/users/12345")                      ->  /api/v1/users/12345   (untouched)
mask_headers({"Authorization": "Bearer ghp_..."})            ->  [REDACTED:authorization]
mask_headers({"Accept": "application/json"})                 ->  application/json        (untouched)
```

**Tests: 114 passed / 10 failed -> 124 passed / 0 failed.**

## When to Use

- Any service that writes request paths, headers, or JSON payloads to logs.
- Pair with `tiny-router` v0.7.3 (`redact_path_middleware()`) and v0.7.4
  (`redact_headers_middleware()`) to cover the route layer.
- Pair with `tiny-log` v0.5.x for structured output.
- Not a replacement for scoped credentials, TLS, or secret storage.

## API Reference (carried forward from the v0.1.0 guide)

The v0.1.0 core surface is unchanged and still current. These four functions
remain the entry points most callers use:

```python
from tiny_secret_mask import (
    SecretMask, MaskRule,        # custom rules
    mask_string, mask_dict, mask_json, mask_response,
)
```

- `mask_string(text)` — regex redaction with JWT, cloud-key, PII,
  card-with-Luhn, hash, and entropy heuristics.
- `mask_dict(d)` — recursive walk; masks values whose **keys** are sensitive
  (`password`, `token`, `secret`, `cookie`, `api_key`, ...).
- `mask_json(blob)` — parse -> redact -> re-emit, preserving structure.
- `mask_response(body, headers=...)` — drop-in for HTTP frameworks; redacts
  both body and Authorization-style headers.
- `safe_repr(obj, max_len=, depth=)` (v0.2.0) — bounded `repr()` that caps
  length and recursion and detects cycles.
- `redact_jsonl(stream)` (v0.2.0) — NDJSON streaming redactor.
- `mask_route_path(path)` (v0.4.0) / `mask_headers(dict)` (v0.5.0) — the two
  sidecars whose packaging defect this release fixes.

### Pluggable Rules

```python
from tiny_secret_mask import SecretMask, MaskRule
import re

mask = SecretMask(rules=[
    MaskRule(name="internal_id", pattern=re.compile(r"\bINT-\d{6}\b"),
             replacement="[REDACTED:internal_id]"),
])
mask_string("Order INT-442109 shipped", mask=mask)
# 'Order [REDACTED:internal_id] shipped'
```

### Coverage Matrix

| Class | Examples |
|-------|----------|
| Bearer/Basic/Token | `Authorization: Bearer ...`, `Basic ...`, `Token ...` |
| JWT | three-segment, structural validation |
| Cloud creds | AWS `AKIA...`, GitHub `ghp_/ghu_/github_pat_`, Stripe `sk_live_/sk_test_`, OpenAI `sk-`/`sk-proj-`, Google `AIza`, Slack `xox[abprs]-` |
| PEM/DER/PGP | full private-key blocks removed |
| PII | emails, IPv4, US-SSN-shaped |
| Payment | card-like with Luhn validation |
| Long opaque | entropy + char-class over 32+ alphanumerics |
| Hash digests | MD5 (32 hex), SHA256 (64 hex) |
| Dict key sensitivity | `password`, `secret`, `token`, `cookie`, `api_key` |
| Route path (v0.4.0) | uuid, hex, AWS, PATs, Slack, Stripe, OpenAI, Google, JWT, base64url catch-all |
| Headers (v0.5.0) | authorization, cookie, set_cookie, x_api_key, x_auth_token |

### When NOT to Use

- Cryptographic secret storage — use a vault.
- Deterministic redaction (round-trip masked <-> original) — this is one-way.
- Compliance-grade scrubbing — pair with audit logging; defense-in-depth only.

### Tests

`124 passing` as of 2026-10-21. Run `python3 -m pytest tests/` after
`pip install -e .`. **Verify the sidecars import from OUTSIDE the repo
directory** — that is exactly the defect this release fixed:

```bash
cd /tmp && python3 -c "import tiny_secret_mask as m; print(m._V040_AVAILABLE, m._V050_AVAILABLE)"
# must print: True True
```

### See Also

- `tools/tiny-route-redact-guide.md` — standalone route-path redactor
- `tools/tiny-headers-redact-guide.md` — standalone header redactor
- `tools/tiny-router-v0.7.3-guide.md` / `tools/tiny-router-v0.7.4-guide.md` —
  middleware integration
- `tools/tiny-log-guide.md` — log sink integration
- `prompts/silent-security-control-audit.md` — audit checklist for degraded
  security primitives
## The Transferable Lesson

> A `try/except ImportError` around a **security** primitive is a design
> smell. It was added for single-file convenience and it converted a hard
> failure into a silent success. Capability degradation is fine for optional
> formatting; it is not fine for a control whose entire job is to be
> unfalsifiable.
>
> The tell: the fallback returned *plausible output* rather than *raising*.
> If `mask_*` had raised, the bug would have been found in one run. Because
> it returned the input, every test that did not assert the redaction tag
> passed.
