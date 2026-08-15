---
name: tiny-mcp-observability
description: "MCP server with built-in tracing, metrics, and span recording for AI agent pipelines. Zero deps, 550 LOC. Last verified: 2026-08-15."
---

# tiny-mcp-observability Guide

> Tracing, metrics, and span recording for AI agent pipelines — zero dependencies, one file.
> GitHub: https://github.com/hussain-alsaibai/tiny-mcp-observability

## What It Does

`tiny-mcp-observability` is an **MCP server** that instruments your agent pipeline — every tool call, LLM call, and span is recorded. Query it via MCP tools: `list_traces`, `get_trace`, `get_metrics`, `export_spans`.

## Features

- **Span trees** — hierarchical spans: agent → LLM → tool → sub-tool
- **Trace recording** — every trace stored, queryable, exportable
- **Metrics aggregation** — per-name stats: count, avg/min/max latency, error rate, tokens, cost
- **MCP tools** — `start_trace`, `start_span`, `end_span`, `list_traces`, `get_trace`, `get_metrics`, `export_spans`, `clear`
- **Decorator API** — `@observe("my_func")` auto-instruments any function
- **LRU eviction** — bounded at 10,000 traces, never leaks memory
- **LLM-aware** — token + cost tracking per span
- 550 LOC, zero dependencies, MIT

## Use Cases

- Replace LangSmith for local/dev environments (zero cost, no account setup)
- Lightweight alternative to OpenTelemetry SDK (6+ deps vs 0)
- Queryable traces instead of opaque log files
- Export spans to JSON/NDJSON for analysis

## Quick Start

```python
from tiny_mcp_observability import observe, get_metrics

@observe("classify_email")
def classify_email(email_text):
    # This span is automatically recorded
    return llm.classify(email_text)

# Query what happened
metrics = get_metrics()
```

Run as MCP server:
```bash
python -m tiny_mcp_observability
```
