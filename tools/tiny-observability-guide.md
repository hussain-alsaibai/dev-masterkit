# tiny-observability — Zero-Dep Structured Observability

## Repo
https://github.com/hussain-alsaibai/tiny-observability

## One-liner
Structured JSON logs + distributed tracing + metrics in one file. Zero
dependencies. ~170 LOC. MIT. A lightweight stand-in for otel/structlog.

## Status
**Repo does not exist upstream yet** (`https://github.com/hussain-alsaibai/tiny-observability`
-> HTTP 404, checked 2026-10-23). Local clone only.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_observability import obs`
and called `obs.start_span(...)` / `obs.log(...)` / `obs.end_span()` on a
**module-level singleton**. **There is no module-level `obs`.** Verified
against the local clone:

```
class TinyObservability:
    __init__(self, service_name: str = "app")
    .log(self, level: str, msg: str, **kwargs)
    .start_span(self, name: str, trace_id: str = None)
    .end_span(self)
```

You construct a **`TinyObservability`** instance. The singleton pattern the old
guide described was never real.

## Quick Example
```python
from tiny_observability import TinyObservability

obs = TinyObservability(service_name="ingest")

obs.start_span("data_fetch")
obs.log("INFO", "Fetching from API", url="https://api.example.com")
# ... work ...
obs.end_span()
```

## Key Features
- Structured JSON logs (stdout, NO_COLOR aware)
- Distributed tracing with trace/span IDs
- Auto-calculated span durations
- No external deps — pure stdlib

## Related
- `tools/tiny-log-guide.md` — `tiny-log`, the richer structured logger
- `tools/tiny-trace-guide.md` — `tiny-trace`, OTel-compatible tracing
