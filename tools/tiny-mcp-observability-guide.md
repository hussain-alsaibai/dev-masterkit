# tiny-mcp-observability Guide

## Repo
https://github.com/hussain-alsaibai/tiny-mcp-observability

## What It Does

Zero-dependency tracing and metrics for MCP servers. One file, no setup. Span
recording, metric counters, and a drop-in server wrapper.

## Last Verified
2026-10-24 (35/35 by test run)

## Three real defects fixed (2026-10-24)

The module shipped with **no test file at all**, and CI ran
`pytest tiny_mcp_observability.py` — which collects **0 items** and exits **5**
(no tests collected). The badge was red for a reason unrelated to the module.

Writing 35 tests surfaced three genuine bugs:

1. `defaultdict(Metric)` called `Metric()` with no arguments, but
   `Metric.name` is a required field — so **every** `end_span()` raised
   `TypeError: Metric.__init__() missing 1 required positional argument`.
   **Metrics were never recorded at all.**
2. `export_spans()` passed raw `Span` dataclasses to `json.dumps(default=str)`,
   which fell back to `str(span)`. **Exports were lists of Python reprs, not
   JSON objects.**
3. `Observed.__call__` wrapped coroutine functions with a *synchronous*
   wrapper, returning an un-awaited coroutine. The span closed before the body
   ran, so **async failures were never recorded** and `error_rate` stayed
   `0.0` for every async call.

Verified: 18 of the new tests fail against the original module; all 35 pass
after the fixes. Suite was absent -> 35.

See `prompts/ci-target-must-match-repo-layout.md` — a repo with no tests is
not a repo with passing tests.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_mcp_observability import
observe, get_metrics`. **`get_metrics` does not exist.** Verified against
upstream `tiny_mcp_observability.py`:

```
SpanStatus, SpanKind, Span, Metric, Store, Observed,
start_span, end_span, observe, get_store, MCPServer
```

The accessor is **`get_store()`**; metrics and spans are read off the returned
`Store`. `MCPServer` is the drop-in wrapper.

## Quick Start

```python
from tiny_mcp_observability import observe, get_store, start_span, end_span

with observe("tool_call", name="search"):
    ...

store = get_store()
print(store.spans)
print(store.metrics)
```

`start_span()` / `end_span()` are the explicit (non-context-manager) form.

## When to Use

- Instrumenting an MCP server so tool calls show up as spans and counters
- Measuring latency and error rate per tool without an OpenTelemetry dependency
- Pairing with `tiny-mcp-audit` for the static half of MCP assurance

## CI defect fixed 2026-10-26

**PEP 604 annotations (`str | None`) are 3.10+, while the package metadata
claimed `>=3.9`.** On 3.9 that raises `TypeError: unsupported operand
type(s) for |` **at import time** — so the whole package was unusable, not
merely degraded.

Fixed with `from __future__ import annotations` at the top of the module,
which defers annotation evaluation.

**35 tests passing** (verified by run 2026-10-26).

> **A version-specific syntax is a runtime failure, not a typing detail.**
> `from __future__ import annotations` is a one-line fix for an entire class
> of it — see `prompts/python-support-is-a-claim.md`.

## Related

- `tools/tiny-mcp-audit-guide.md` — static manifest auditing (the other half)
- `tools/tiny-mcp-registry-guide.md` — cataloguing MCP servers
- `tools/tiny-trace-guide.md` — general tracing primitives
