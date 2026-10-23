# tiny-mcp-observability Guide

## Repo
https://github.com/hussain-alsaibai/tiny-mcp-observability

## What It Does

Zero-dependency tracing and metrics for MCP servers. One file, no setup. Span
recording, metric counters, and a drop-in server wrapper.

## Last Verified
2026-10-23

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

## Related

- `tools/tiny-mcp-audit-guide.md` — static manifest auditing (the other half)
- `tools/tiny-mcp-registry-guide.md` — cataloguing MCP servers
- `tools/tiny-trace-guide.md` — general tracing primitives
