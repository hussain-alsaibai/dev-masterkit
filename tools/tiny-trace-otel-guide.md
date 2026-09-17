# tiny-trace-otel — Stdlib-Only OTLP/HTTP Tracing Exporter

> The smallest way to ship OpenTelemetry-compatible spans from Python without the ~6MB `@opentelemetry/exporter-trace-otlp-http` package.
> Last verified: 2026-09-17 | Version 0.1.0 | hussain-alsaibai/tiny-trace-otel

## What It Is

A single-file (~440 LOC) Python OTLP/HTTP tracing exporter that ships spans to Honeycomb, SigNoz, Grafana Cloud Tempo/Loki, Datadog (via otel-collector), New Relic, Jaeger, or any OTLP/HTTP consumer — same JSON envelope as the official SDK.

- W3C Trace Context (`traceparent`, `tracestate`) propagation
- OTLP/HTTP JSON wire format — drop-in compatible with OTel collectors
- Batch span processor with `max_batch_size` and `export_interval_seconds`
- Span attributes + events + parent/child context
- Stdlib only — no `protobuf`, no `grpcio`
- 25/25 tests passing, MIT

## Why It Exists

The official `@opentelemetry/exporter-trace-otlp-http` package pulls ~6 MB of transitive deps just to POST a JSON envelope over HTTP. For an agent service that wants to ship spans to its own collector or to a SaaS provider, that's overkill.

`tiny-trace-otel` ships:
- W3C Trace Context propagation
- OTLP/HTTP JSON envelope
- Batching with back-pressure
- `service.name` / `service.version` resource attrs
- Zero third-party deps

## Repo

https://github.com/hussain-alsaibai/tiny-trace-otel

## When to Use

- You want OpenTelemetry tracing without the 6 MB exporter package
- You need a stdlib-only way to instrument cron jobs / agent loops
- You're wiring per-call spans into `tiny-llm-router` (one-line hook)
- You ship spans to Honeycomb, SigNoz, or any OTLP/HTTP consumer

## Minimal Example

```python
from tiny_trace_otel import Tracer, BatchSpanProcessor, OTLPHttpExporter, set_processor

exporter = OTLPHttpExporter(
    endpoint="https://api.honeycomb.io/v1/traces",
    headers={"x-honeycomb-team": "YOUR_API_KEY"},
)

processor = BatchSpanProcessor(exporter, max_batch_size=64, export_interval_seconds=2.0)
set_processor(processor)

tracer = Tracer(
    name="myagent.tiny-trace-otel",
    resource_attrs={"service.name": "bounty-hunter", "service.version": "1.0.0"},
)

with tracer.start_span("scan-issues") as span:
    span.set_attribute("issues.scanned", 22)
    span.add_event("checkpoint", stage="initial-pass")
    results = find_targets()
    span.set_attribute("issues.found", len(results))
```

## Tested Patterns

- Honeycomb + SigNoz + Grafana Cloud Tempo end-to-end
- Parent/child context propagation through `with` blocks
- Batch flush on shutdown
- Fail-soft when endpoint unreachable (drops batch, continues)

## See Also

- `tools/tiny-llm-router-guide.md` — pair the two for per-LLM-call spans
- `tools/cost-tracker.md` — combine traces with spend ledger
