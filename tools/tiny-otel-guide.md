# tiny-otel - Zero-Dependency OTLP/HTTP Trace Exporter

## Repo
https://github.com/hussain-alsaibai/tiny-otel

## One-liner
Zero-dependency OTLP/HTTP trace exporter for Node agents that ships the OpenTelemetry `ExportTraceServiceRequest` JSON envelope to any collector that accepts OTLP.

## Install
```bash
npm install tiny-otel
```

## Quick Example

```js
import { TinyTracer } from "tiny-otel";

const tracer = new TinyTracer({
  serviceName: "daily-cron-agent",
  endpoint: "http://localhost:4318/v1/traces"
});

await tracer.inSpan("repo.update", async (span) => {
  span.setAttribute("repo.name", "dev-masterkit");
  span.setAttribute("cron.id", "daily-dev-masterkit-update");

  await updateRepo();
});

await tracer.flush();
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector base URL or `/v1/traces` endpoint |
| `OTEL_EXPORTER_OTLP_HEADERS` | Comma-separated `key=value` headers |
| `OTEL_SERVICE_NAME` | Service name in resource attributes |

## Span helpers

| Helper | Use |
|--------|-----|
| `inSpan(name, asyncFn)` | Wrap async work and auto-close the span |
| `setAttribute(key, value)` | Encode string, int, double, bool, array, or kvlist values |
| `recordException(error)` | Add OpenTelemetry exception event and set ERROR status |
| `flush()` | Send any buffered spans before process exit |

## Export behavior

`tiny-otel` sends the OTLP v1.5.0 JSON shape:

```json
{
  "resourceSpans": [
    {
      "resource": { "attributes": [] },
      "scopeSpans": [
        {
          "scope": { "name": "tiny-otel" },
          "spans": []
        }
      ]
    }
  ]
}
```

Collectors that speak OTLP/HTTP can accept that payload directly, including Honeycomb, Tempo, SigNoz, Datadog through the OpenTelemetry Collector, and Jaeger through OTLP.

## Agent workflow fit

Use `tiny-otel` when an autonomous Node process needs real traces without pulling in the official OpenTelemetry dependency tree:

- wrap each cron task in a top-level span
- annotate model/tool calls with provider, model, cost, retry count, and decision ids
- record exceptions before retry logic swallows them
- flush before process exit so short-lived jobs do not lose spans

## Testing

- **10/10 tests passing**
- Includes a real HTTP server integration test
- Fetch is injected through options for clean tests; no global monkey-patching
- 0 runtime dependencies

## Verified limitations

- Current scope is trace export, not metrics or logs.
- W3C trace context propagation is not implemented yet on the Node side; use `tiny-trace` in Python when propagation is required today.

Last verified: 2026-07-07
