# tiny-trace — Zero-Dependency OpenTelemetry-Compatible Tracing

## Repo
https://github.com/hussain-alsaibai/tiny-trace

## One-liner
OpenTelemetry-API-compatible subset. W3C `traceparent` / `tracestate` propagation,
4 samplers (AlwaysOn/Off, TraceIdRatio, ParentBased), 3 exporters (Console, InMemory, JSONL).

## Install
```bash
pip install tiny-trace
```

## Quick Example

```python
from tiny_trace import tracer, ConsoleExporter, AlwaysOn

tracer.set_exporter(ConsoleExporter())
tracer.set_sampler(AlwaysOn())

with tracer.start_as_current_span("http.request") as span:
    span.set_attribute("http.url", url)
    span.set_attribute("http.status", resp.status_code)
    resp = fetch(url)

# W3C propagation across services
headers = {"traceparent": tracer.current_traceparent()}
# ...on the other side:
ctx = tracer.extract({"traceparent": incoming})
with tracer.start_as_current_span("downstream", parent=ctx):
    ...
```

## Components

| Component | What it does |
|-----------|--------------|
| `Tracer` / `tracer` | Global tracer instance; `start_as_current_span` context manager |
| `AlwaysOn` / `AlwaysOff` | Sample every span or none |
| `TraceIdRatio(rate)` | Probabilistic sampling |
| `ParentBased(root)` | Honor parent's sampling decision |
| `ConsoleExporter` | Pretty-prints to stdout (dev) |
| `InMemoryExporter` | Holds spans in a list (tests) |
| `JSONLExporter` | Append-only JSON-Lines file (prod-friendly) |

## W3C `traceparent` format

```
00-<32hex-trace-id>-<16hex-span-id>-<2hex-flags>
```

- Version field: must be `00`. Anything else → parent is ignored (`INVALID_SPAN_CONTEXT`).
- Flags: `01` = sampled, `00` = not sampled.
- IDs must be valid hex; reject any non-hex input.

## Testing

- **57/57 tests passing**
- 802 LOC + 537 test LOC
- 0 dependencies, 0 transitive deps
- Includes a W3C-spec sample validating `traceparent` round-trips

## Gotcha — invalid `traceparent` must not be used silently

The first implementation required 4 components but didn't validate `version == "00"`.
Invalid parents (e.g. version `ff`) silently got used as if they were valid.

```python
# Wrong
m = re.match(r"^([0-9a-f]{2})-([0-9a-f]{32})-...$", s)
if m: return SpanContext(...)

# Right
if version != "00":
    return INVALID_SPAN_CONTEXT
```

Last verified: 2026-07-02
