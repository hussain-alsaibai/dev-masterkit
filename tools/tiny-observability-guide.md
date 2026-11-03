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
2026-11-03 12:25 UTC - `GET /repos/hussain-alsaibai/tiny-observability`
**still returns HTTP 404** (authenticated request, re-checked). Local clone
only. The same claim was re-verified on 2026-11-02 and has held unchanged
across three checks, so it is one of the two "local only" claims in this
repo that is still true.

> **Note the timestamp.** `Last Verified` here names the *moment*, not the
> day - see `prompts/a-date-is-a-timestamp-not-a-property.md`. Two other
> guides in this repo carried the same 404 wording with the same date and
> were wrong by 17:10 UTC that same afternoon.

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
