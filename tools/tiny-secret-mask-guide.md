# tiny-secret-mask v0.1.0 — Stdlib-Only Secret Redaction

> Single-file, zero-dependency secret redaction for logs, HTTP responses, and JSON payloads. ~430 LOC, Python 3.8+, MIT.
> Last verified: 2026-09-24 | Version 0.1.0 | hussain-alsaibai/tiny-secret-mask

## Why It Exists

Stop leaking credentials, tokens, and PII into log files, error sinks, or LLM context windows. Every leak pattern (`Authorization: Bearer …`, `ghp_…`, `sk-…`, JWTs, PEM blocks, emails, card numbers with Luhn, hash digests) is matched structurally so false positives stay low.

## Repo

https://github.com/hussain-alsaibai/tiny-secret-mask

## Public API (8 surface functions)

```python
from tiny_secret_mask import (
    SecretMask, MaskRule,        # custom rules
    mask_string, mask_dict, mask_json, mask_response,
)
```

- `mask_string(text)` — regex-based redaction with JWT, cloud-key, PII, card-with-Luhn, hash, and entropy heuristics.
- `mask_dict(d)` — recursively walks dicts; masks values whose **keys** match sensitive patterns (`password`, `token`, `secret`, `cookie`, `api_key`, …).
- `mask_json(blob)` — parse → redact → re-emit (preserves structure).
- `mask_response(body, headers=...)` — drop-in for HTTP frameworks; redacts both body and Authorization-style headers.

## Pluggable Rules

```python
from tiny_secret_mask import SecretMask, MaskRule
import re

mask = SecretMask(rules=[
    MaskRule(name="internal_id", pattern=re.compile(r"\bINT-\d{6}\b"), replacement="[REDACTED:internal_id]"),
])
mask_string("Order INT-442109 shipped", mask=mask)
# 'Order [REDACTED:internal_id] shipped'
```

## Drop-in Patterns for the tiny-* Ecosystem

- **`tiny-router`** — wrap responses in `mask_response()` before returning to clients; mask Authorization headers on inbound.
- **`tiny-log`** — feed log lines through `mask_string()` before writing to disk or shipping to a remote sink.
- **`tiny-llm`** — `mask_dict(messages)` before sending conversation history to a model.
- **`tiny-trace-otel`** — span attributes scrubbed via `mask_dict()` to keep secrets out of Jaeger/Tempo.

## Coverage Matrix

| Class                | Examples                                           |
|----------------------|----------------------------------------------------|
| Bearer/Basic/Token   | `Authorization: Bearer …`, `Basic …`, `Token …`    |
| JWT                  | Three-segment, structural validation               |
| Cloud creds          | AWS `AKIA…`, GitHub `ghp_/ghu_/github_pat_…`, Stripe `sk_live_/sk_test_`, OpenAI `sk-…`/`sk-proj-…`, Google `AIza…`, Slack `xox[abprs]-…` |
| PEM/DER/PGP blocks   | Full private-key blocks removed                    |
| PII                  | Emails, IPv4, US-SSN-shaped                        |
| Payment              | Card-like with Luhn validation                     |
| Long opaque          | Entropy + char-class over 32+ alphanumerics        |
| Hash digests         | MD5 (32 hex), SHA256 (64 hex)                      |
| Dict key sensitivity | `password`, `secret`, `token`, `cookie`, `api_key` |

## When to Use

- Redacting logs before they hit a remote sink
- Cleaning HTTP responses/headers in agent callback handlers
- Scrubbing dict/JSON payloads before LLM calls
- Anywhere secrets could leak into stdout, error reports, or telemetry

## When NOT to Use

- Cryptographic secret storage — use a vault.
- Deterministic redaction (where you need to round-trip masked ↔ original) — this is one-way.
- Compliance-grade scrubbing — pair with audit logging; this is a defense-in-depth layer.

## Tests

`tests/` covers each pattern class (positive + negative), Luhn boundary cases, JWT structural validation, dict recursion, custom rules, and integration with `mask_response()`. Run `python -m pytest tests/` after `pip install -e .`.

## See Also

- `tools/tiny-router-v0.4-guide.md` — pair with `mask_response()` for HTTP handler redaction
- `tools/tiny-secret-guide.md` — generic secret handling notes
- `tools/tiny-log-guide.md` — log sink integration
