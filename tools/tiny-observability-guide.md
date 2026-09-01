# tiny-observability — Zero-Dep Structured Observability

## Repo
https://github.com/hussain-alsaibai/tiny-observability

## One-liner
Structured JSON logs + distributed tracing + metrics in one file. Zero dependencies.
~170 LOC. MIT. Replaces otel/structlog for lightweight use cases.

## Install
```bash
pip install tiny-observability
# Or: copy tiny_observability.py directly
```

## Quick Example
```python
from tiny_observability import obs

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

## Last Verified
2026-09-01
