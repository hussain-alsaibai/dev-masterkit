# tiny-metrics — Zero-Dependency Prometheus-Compatible Metrics

## Repo
https://github.com/hussain-alsaibai/tiny-metrics

## One-liner
Prometheus exposition format (Counter, Gauge, Histogram, Summary) with `/metrics` HTTP endpoint, default collectors, label sanitisation, and decorator timing helpers. `prometheus_client` in one file.

## Install
```bash
pip install tiny-metrics
```

## Quick Example

```python
from tiny_metrics import Counter, Histogram, start_http_server

REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "code"])
LATENCY  = Histogram("http_request_duration_seconds", "Request latency",
                     buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5))

@LATENCY.time()
def handle(method, path):
    # ...
    REQUESTS.labels(method=method, code=200).inc()

# Mount /metrics on port 8000
start_http_server(8000)
```

Scrape with Prometheus:
```
http://localhost:8000/metrics
```

## Metrics types

| Type | Use |
|------|-----|
| `Counter` | Monotonic increasing values (request count, error count) |
| `Gauge` | Values that go up and down (memory, queue depth, active conns) |
| `Histogram` | Bucketed observations (request latency, response size) |
| `Summary` | Quantile-estimated observations (p50/p95/p99 latency) |

## Histogram timing

```python
@LATENCY.time()
def handle(...):
    ...

# or as a context manager:
with LATENCY.time():
    do_work()

# manual observation:
LATENCY.observe(elapsed_seconds)
```

## Default collectors

| Collector | Metrics |
|-----------|---------|
| `ProcessCollector(registry)` | `process_cpu_seconds_total`, `process_resident_memory_bytes`, `process_virtual_memory_bytes`, `process_open_fds`, `process_max_fds`, `process_start_time_seconds` |
| `PlatformCollector(registry)` | `python_info{version=…, implementation=…}` (always 1) |

## Custom collectors

```python
from tiny_metrics import REGISTRY, Gauge

class MyCollector:
    def collect(self):
        g = Gauge("queue_depth", "Pending jobs")
        g.set(get_queue_depth())
        yield g

REGISTRY.register_collector(MyCollector())
```

## Properties

| Property | How |
|----------|-----|
| Format | OpenMetrics 0.0.4 text (`# HELP`, `# TYPE`, `# EOF`) |
| Endpoints | `/metrics` (text), `/` (help) |
| Label safety | escapes `"`, `\n`, `\` per spec |
| Multi-process | Not supported (use multiple processes with a sidecar or scrape each) |
| Buckets | User-configurable for Histogram; sane defaults available |

## Testing

- **32/32 tests passing**
- 5 test categories (counter/gauge math, histogram buckets, summary quantiles,
  label sanitisation, exposition format)
- 0 dependencies, 0 transitive deps
- 1 file
- ~980 LOC

## Gotcha — integer-valued floats must render as `1`, not `1.0`

Histogram bucket boundaries can be floats (`0.005`, `0.01`). But integer buckets
like `1`, `2`, `5` are still typed `float`. Prometheus convention renders
integer-valued floats without a decimal point: `"1"`, not `"1.0"`. Scrapers will
parse `1.0` correctly, but dashboards and rules using `le="1"` may break.

**Fix:** in `_format_bucket(le)`, render `int(le)` when
`le == int(le) and abs(le) < 1e15`.

```python
def _format_bucket(le: float) -> str:
    if le == float("inf"):
        return "+Inf"
    if le == int(le) and abs(le) < 1e15:
        return str(int(le))
    return repr(le)
```

## Gotcha — singleton registries need per-test isolation

`tiny_metrics.REGISTRY` is a module-level singleton. Two tests that both
create `Counter("foo", ...)` collide — the second creation raises `DuplicateMetric`.

**Fix pattern:** every test gets a fresh registry:

```python
def fresh_registry():
    from tiny_metrics.registry import MetricRegistry
    return MetricRegistry()

def test_counter_increments():
    reg = fresh_registry()
    c = Counter("foo", "help", registry=reg)
    c.inc()
    assert c.value == 1
```

The same pattern applies to `tiny-flags`, `tiny-cron`'s `Scheduler`, and any
plugin with global state. Pick one of: per-test reset, per-test fixture, or
per-test new instance. Consistency beats cleverness.

## Gotcha — `Future.result(timeout=…)` does not cancel the worker

`Histogram.time()` uses a `ThreadPoolExecutor` for cross-thread timing.
The `future.result(timeout=N)` cuts off the *wait* but the worker keeps
running until your function returns. The thread is a daemon in the shared
pool, so it dies with the process — but the *measurement is lost*, not
the work.

For sub-millisecond accuracy, use `Histogram.time()` synchronously
in the same thread, or use a `Summary` with `observe()` from a context
manager.

## Related ecosystem

- **`tiny-trace`** — when you want to correlate `trace_id` in metric labels
- **`tiny-rate`** — counter-style "tokens remaining" gauge
- **`tiny-pool`** — gauge for active workers
- **`tiny-queue`** — gauge for `pending`/`inflight`/`dead` job counts

Last verified: 2026-07-04