# tiny-tool-result Guide

> Normalized, validated, redacted, and truncated tool-call result envelopes for AI agents. ~360 LOC, 51 tests, stdlib-only.
**Last verified: 2026-10-25** — 51 tests passing, verified by run.

**Repo:** `github.com/hussain-alsaibai/tiny-tool-result`
**Version:** 0.2.0 (2026-10-10, re-verified 2026-10-24, re-verified 2026-10-25 — 51 passed by run)
**Previous version:** 0.1.0 (basic envelope + `@wrap` decorator) — replaced by this version.
**Author:** OpenClaw (autonomous cron, daily-bounty-workflow context)
**Status:** ✅ Stable — 51/51 tests passing (verified by run 2026-10-24, up from 38). Breaking change from 0.1.0 (decorator API → functional builders). No external users yet.

## Credential redaction fix (2026-10-24)

**A real secret-leak bug, found while triaging an unrelated WIP.** The old
scrubber matched the key and then consumed exactly one whitespace-delimited
token:

```
failure("Authorization: Bearer ***")
-> "Authorization=***] abc123"     # the token survived
```

It redacted the word `Bearer` and left the credential itself in the message. A
failure message is exactly what gets logged and sent to an LLM, so this leaked
secrets into logs and model context.

Replaced with `_scrub_secrets()`:

- recognises auth schemes (bearer / basic / token / digest) and consumes the
  whole credential span up to the next field boundary
- covers more credential keys (`password`, `secret`, `client_secret`,
  `access_token`, `refresh_token`, `private_key`, …)
- leaves ordinary error text untouched

**Verified by reverting the fix in a scratch copy:** the 6 new regression tests
fail against the old code and pass against the new.

Also fixed in the same WIP: `success()` passed `kind="json"` explicitly *and*
forwarded `**meta`, so `text_result()` raised `TypeError: got multiple values
for keyword argument 'kind'`; numeric schema violations reported `">= 0"`
instead of naming the constraint; and two test bugs (a dict `approx_tokens`
counting its keys, and a pattern test writing `-d+` where it meant digits).

Suite 43 → 51.

---

## What is it?

`tiny-tool-result` is a single-file Python library (~360 LOC) that wraps any return value from a tool call into a uniform `ToolResult` envelope with one consistent shape:

```python
{
  "ok": bool,
  "value": Any,
  "error": str | None,
  "tool": str,
  "latency_ms": float,
  "tokens": int,
  "trace_id": str | None,
  "span_id": str | None,
  "retryable": bool,
  "retry_after": float,
  "truncated": bool,
  "redacted": list[str],
  "validation_errors": list[str],
  "valid": bool,
}
```

The envelope handles the four messy realities of every agent tool call in one place:

- **Schema validation** — built-in mini-validator (no `jsonschema` dep)
- **Size limiting** — `max_bytes` auto-truncates with explicit `[TRUNCATED: 12.4KB of 387KB shown]` marker
- **Secret redaction** — recursive glob (`redact_keys=["*.password", "headers.Authorization"]`)
- **Multi-modal bundling** — `image_result()`, `text_result()`, `multi_result()` for mixed outputs

See the [Developer Tools Landscape 2026-10-10](../../dev-reports/2026-10-10-developer-tool-trends.md) report (Pattern 1: "the envelope pattern") for the cross-ecosystem context.

## Why does it exist?

In 2026 every AI agent hits the same wall. Tool calls return shapes that don't match the schema, dump 400 KB of JSON into the next prompt, leak `Authorization` headers in error messages, or contain base64 images the model can't actually see. Teams write a pile of ad-hoc `if isinstance(...)` handlers and live with it.

`tiny-tool-result` replaces the pile with one normalized envelope, with the same shape regardless of whether the underlying call returned JSON, text, an image, or a partial failure. The LLM doesn't care which library wrote the envelope; it just sees `{ok, value, error, tool, latency_ms, tokens, ...}` and reasons.

## Why 0.2.0 replaces 0.1.0

The 0.1.0 envelope used a `@wrap` decorator pattern. In practice the decorator hid the redaction / truncation / validation pipeline — callers couldn't see which calls had been sanitized. The 0.2.0 functional builders (`success()`, `failure()`, `image_result()`, `multi_result()`) make the pipeline explicit. Breaking change, but no external users yet.

## Usage

```python
from tiny_tool_result import success, failure, image_result, multi_result, ToolResult

# Wrap any return value
r = success({"user_id": 42, "name": "ada"},
            tool="db.lookup",
            latency_ms=12,
            max_bytes=4096,
            redact_keys=["*.password", "Authorization"],
            schema={"type": "object", "required": ["user_id"]})

if r.ok and r.valid:
    send_to_llm(r.summary())        # redacted, truncated, JSON-safe
else:
    for err in r.validation_errors:
        log("schema mismatch", err)

# Failure with retry hint — error is auto-scrubbed of secrets
r = failure("Connection refused", tool="api.fetch", retryable=True, retry_after=2.0)

# Multi-modal
r = multi_result(text="see below",
                 image_b64="iVBORw0KGgoAAAANSUhEUgAA...",
                 data={"score": 0.97})

# Async twins
from tiny_tool_result import asuccess, afailure
r = await asuccess(await_call())
```

## API Reference

### Helpers

- `success(value, tool=..., max_bytes=..., redact_keys=..., schema=..., latency_ms=..., **meta)` — wrap success
- `failure(error, tool=..., retryable=False, retry_after=0, **meta)` — wrap failure (error is secret-scrubbed)
- `image_result(b64, mime="image/png", caption="")` — multi-modal image
- `text_result(text, tool=...)` — plain text envelope
- `multi_result(text=None, image_b64=None, data=None, **meta)` — bundle mixed outputs
- `asuccess` / `afailure` — async twins of `success` / `failure`
- `is_success(r)` / `is_failure(r)` — type guards

### `ToolResult` methods

- `r.summary()` — short, prompt-safe string (truncated + redacted)
- `r.to_dict()` — JSON-serializable
- `r.approx_tokens()` — char/4 heuristic estimate

### JSON Schema mini-validator

Supported subset (no `jsonschema` dependency):

| Keyword | Notes |
|---------|-------|
| `type` | `object`, `array`, `string`, `number`, `integer`, `boolean`, `null` |
| `required` | list of required property names |
| `properties` | per-property schema |
| `items` | array element schema |
| `enum` | exact-value list |
| `minLength` / `maxLength` | string length |
| `minimum` / `maximum` | numeric bounds |
| `pattern` | regex match |

## Configuration

`max_bytes=0` disables truncation. `redact_keys=[]` disables redaction. `schema=None` disables validation. All three defaults are sensible: nothing happens unless you opt in.

## Cross-Repo Interop

`tiny-tool-result` is part of the **OpenClaw developer tools ecosystem**:

- **tiny-retry-plus** — `failure(..., retryable=True, retry_after=2.0)` is the contract; the retry layer consumes it
- **tiny-trace / tiny-trace-otel** — `trace_id` / `span_id` flow in automatically
- **tiny-cost** — `latency_ms` + `tokens` feed the cost ledger
- **tiny-router** — `Route.to_openapi_schema` produces the matching JSON Schema for the `schema=` argument
- **tiny-secret-mask** — redaction is delegated to the same rule catalogue
- **tiny-agent-scope** — `tool` field maps to `scope.record_tool_call(tool, ...)`
- **dev-masterkit** — the curated collection; this guide lives there

## Adoption Path

1. `pip install tiny-tool-result`
2. Replace `return result` with `return success(result, tool="...")` in your tool implementations
3. Add `max_bytes=N` to calls that fetch big payloads
4. Add `redact_keys=["Authorization", "*.password"]` to any tool that touches user data
5. Add `schema={...}` to calls that feed an LLM prompt directly
6. Replace `if result: ...` with `if r.ok and r.valid: ...`
7. Wire `r.summary()` into the LLM prompt instead of `r.to_dict()` to keep tokens under control

## Roadmap (next 7 days)

- `tiny-tool-result` v0.2.1 — bug-fix release if any zero-dep issues surface
- `tiny-tool-result` v0.3.0 — async streaming variant (`astream_success`)
- `dev-masterkit` — add a `tiny-tool-result`-aware example skill to `skills/`

## See also

- [dev-reports/2026-10-10-developer-tool-trends.md](../../dev-reports/2026-10-10-developer-tool-trends.md) — "The envelope pattern" (Pattern 1)
- [tiny-skill-loader-guide.md](./tiny-skill-loader-guide.md) — runtime plugin system that mounts tools `tiny-tool-result` wraps
- [tiny-agent-scope-guide.md](./tiny-agent-scope-guide.md) — budget / policy layer that gates every tool call
- [MEMORY.md](../../MEMORY.md) — Tiny-* stack overview (50+ repos)
