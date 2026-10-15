# tiny-secret-mask v0.5.0 — HTTP Header Redaction Sidecar

> Zero-dependency credential redaction library. v0.5.0 ships `mask_headers(headers)`, `HeaderRedactor`, `MaskHeaderRule`, and a 16-rule catalogue for HTTP request/response headers. Sidecar module `tiny_secret_mask_v050.py` (~175 LOC) is lazy-imported at install time.
> Last verified: 2026-10-15 | Version 0.5.0 | hussain-alsaibai/tiny-secret-mask

## What Changed in v0.5.0 (Oct 2026)

- **`mask_headers(headers, *, case_sensitive=False) -> dict`** — replaces credential-bearing header values with `[REDACTED:<rule_name>]` placeholders. Returns a NEW dict; the input mapping is not mutated. Idempotent: a second pass on the redacted dict is a no-op because the placeholder is not a header name.
- **`MaskHeaderRule`** — a configurable rule: a header-name pattern (string or regex) + a replacement function. The rule object composes with the default catalogue.
- **`HeaderRedactor`** — composable engine around `mask_headers` with custom rules. Use `HeaderRedactor.default()` for the production rule set.
- **`HEADER_REDACT_RULES`** — the default 16-pattern catalogue with severity levels (`low | medium | high | critical`).
- **`redact_header_value(name, value, *, case_sensitive=False)`** — single-value redaction; useful when only one header pair is in hand.
- **`header_pattern_names()` / `header_pattern_by_severity(level)`** — query helpers for the catalogue.
- **`install_header_default()`** — bridges the default rule set into custom engines.
- **Sidecar module:** `tiny_secret_mask_v050.py` (~175 LOC). Main file re-exports the new names so `from tiny_secret_mask import mask_headers` works.
- **41 new tests** in `tests/test_v050_additions.py`. Suite passes locally (CI will verify when PAT is restored).

## The 16-Pattern Catalogue

| Severity | Rule Name | Header Pattern | Examples |
|----------|-----------|----------------|----------|
| critical | `authorization` | `^authorization$` | `Authorization` |
| critical | `proxy_authorization` | `^proxy-authorization$` | `Proxy-Authorization` |
| high | `cookie` | `^cookie$` | `Cookie` |
| high | `set_cookie` | `^set-cookie$` | `Set-Cookie` |
| critical | `x_api_key` | `^x-api-key$` | `X-API-Key` |
| critical | `x_auth_token` | `^x-auth-token$` | `X-Auth-Token` |
| high | `x_csrf_token` | `^x-csrf-token$` | `X-CSRF-Token` |
| high | `x_hub_signature` | `^x-hub-signature(-256)?$` | `X-Hub-Signature`, `X-Hub-Signature-256` |
| critical | `x_hub_token` | `^x-hub-token$` | `X-Hub-Token` |
| high | `stripe_signature` | `^stripe-signature$` | `Stripe-Signature` |
| critical | `github_token` | `^x-github-token$` | `X-GitHub-Token` |
| critical | `slack_token` | `^x-slack-token$` | `X-Slack-Token` |
| critical | `shopify_token` | `^x-shopify-access-token$` | `X-Shopify-Access-Token` |
| high | `aws_signature` | `^x-aws-signature$` | `X-AWS-Signature` |
| critical | `aws_security_token` | `^x-aws-security-token$` | `X-AWS-Security-Token` |
| high | `bearer_prefix` | `^bearer$` | `Bearer` |

## Quick Start

```python
from tiny_secret_mask import mask_headers

incoming = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9....",
    "X-Request-Id": "abc-123",
    "X-API-Key": "sk_live_51Hx...",
    "Cookie": "session=abc123",
    "User-Agent": "curl/8.0.0",
}

redacted = mask_headers(incoming)
# {
#     "Authorization": "[REDACTED:authorization]",
#     "X-Request-Id": "abc-123",   # unchanged
#     "X-API-Key": "[REDACTED:x_api_key]",
#     "Cookie": "[REDACTED:cookie]",
#     "User-Agent": "curl/8.0.0",  # unchanged
# }
```

### Custom rule

```python
from tiny_secret_mask import HeaderRedactor, MaskHeaderRule
import re

redactor = HeaderRedactor(rules=[
    MaskHeaderRule(name="internal_tenant",
                   header_pattern=re.compile(r"^x-tenant-\d+$"),
                   replace=lambda name, value: "[REDACTED:internal_tenant]"),
])

redactor.redact(incoming)
```

### Single-value redaction

```python
from tiny_secret_mask import redact_header_value

redact_header_value("Authorization", "Bearer xyz")  # "[REDACTED:authorization]"
redact_header_value("X-Request-Id", "abc")         # "abc" (unchanged)
```

### Querying the catalogue

```python
from tiny_secret_mask import header_pattern_names, header_pattern_by_severity

header_pattern_names()  # ['authorization', 'proxy_authorization', 'cookie', ...]
header_pattern_by_severity("critical")  # ['authorization', 'proxy_authorization', 'x_api_key', ...]
```

## Why a Sidecar?

Same pattern as v0.2.0, v0.3.0, v0.4.0: the sidecar module (`tiny_secret_mask_v050.py`) ships new functionality as an opt-in import. Users on `tiny-secret-mask < 0.5.0` see no behaviour change when they upgrade — `mask_headers` is only available on v0.5.0+. The `__init__` re-exports the new names so `from tiny_secret_mask import mask_headers` works.

## When to Use / When to Use Something Else

**Use when:**

- You forward, log, or persist HTTP request/response headers
- You need a rule catalogue that's already curated for the common web stacks (OAuth, GitHub, Slack, Stripe, AWS, Shopify, GitHub webhooks)
- You want a counter / observability hook (pair with `tiny-router v0.7.4` or `tiny-headers-redact`)

**Don't use when:**

- You only need body redaction (use `mask_string` from v0.1.0 or wait for the planned v0.6.0 body layer)
- You control the upstream and know no credentials cross the boundary (still good defence in depth)
- You need a custom header set that's not in the 16-pattern catalogue and you don't want the defaults — use `HeaderRedactor(rules=[...])` to construct an empty engine

## The Five-Layer Credential-Leak Loop

v0.5.0 closes the credential-leak loop that v0.4.0 opened with path redaction:

| Layer  | What it protects | Reference |
|--------|------------------|-----------|
| Value  | The credential itself (Bearer, JWT, AWS key) | `mask_string` v0.1.0 |
| Key    | The field name (password, token, api_key) | `mask_dict` v0.2.0 |
| Trace  | The W3C tracestate vendor entries | `mask_trace_context` v0.3.0 |
| Path   | The URL path component (UUID, JWT, AWS key) | `mask_route_path` v0.4.0 |
| Header | The HTTP header (Authorization, Cookie, X-API-Key) | `mask_headers` v0.5.0 |

Any primitive that crosses a network boundary, persists to disk, or emits an observability span is now expected to apply **all five** layers.

## Repo

https://github.com/hussain-alsaibai/tiny-secret-mask

## See Also

- `tools/tiny-router-v0.7.4-guide.md` — `redact_headers_middleware()` integrates the v0.5.0 catalogue at the router layer
- `tools/tiny-headers-redact-guide.md` — framework-agnostic standalone middleware (new repo, no `tiny-router` dependency)
- `tools/tiny-secret-mask-v0.4-guide.md` — `mask_route_path()` and the 12-pattern path catalogue
- `tools/tiny-router-v0.7.3-guide.md` — `redact_path_middleware()` for the path layer
- `tools/tiny-route-redact-guide.md` — framework-agnostic path middleware
