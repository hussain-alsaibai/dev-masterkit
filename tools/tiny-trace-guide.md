# tiny-trace Guide

## Repo
https://github.com/hussain-alsaibai/tiny-trace

## What It Does

Zero-dependency OpenTelemetry-API-compatible tracing. One file, no setup.
W3C trace context, samplers, and pluggable exporters.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_trace import tracer,
ConsoleExporter, AlwaysOn` — including a **module-level `tracer` instance**.
**There is no module-level `tracer`.** Verified against upstream `tiny_trace.py`:

```
__all__ = ['Tracer', 'Span', 'SpanContext', 'TraceFlags', 'SpanKind', 'Status',
           'StatusCode', 'SamplingResult', 'Sampler', 'AlwaysOn', 'AlwaysOff',
           'TraceIdRatio', 'ParentBased', 'Exporter']
```

You construct a `Tracer` yourself. Also note there is **no `ConsoleExporter`**
in `tiny-trace` — see `tiny-trace-otel` for `StdoutExporter`.

## Key Features

- `Tracer` / `Span` / `SpanContext` — the core tracing API
- `SpanKind` / `Status` / `StatusCode` — OTel-compatible enums
- Samplers: `AlwaysOn`, `AlwaysOff`, `TraceIdRatio`, `ParentBased`
- `Exporter` — the exporter interface

## Quick Start

```python
from tiny_trace import Tracer, AlwaysOn, SpanKind

tracer = Tracer(sampler=AlwaysOn(), exporter=my_exporter)

with tracer.start_as_current_span("db.query", kind=SpanKind.CLIENT) as span:
    span.set_attribute("db.system", "postgresql")
    ...
```

## When to Use

- Instrumenting an agent or service when you want OTel-shaped spans without
  the OpenTelemetry dependency
- Propagating W3C `traceparent` across process boundaries
- Sampling decisions you control (unlike most SDK defaults)

## Related

- `tools/tiny-trace-otel-guide.md` — `tiny-trace-otel`, which ships the actual
  `OTLPHttpExporter` and `BatchSpanProcessor`
