# tiny-metrics — Prometheus-Compatible Metrics

## Summary

Zero-dependency Prometheus-compatible metrics library. No external libraries — pure Python stdlib.

## Quick Reference

- **Repo:** [hussain-alsaibai/tiny-metrics](https://github.com/hussain-alsaibai/tiny-metrics)
- **Lines of code:** ~450
- **Tests:** 21 (all passing)
- **Dependencies:** None (stdlib only)

## Core Classes

### `Counter`
Monotonically increasing integer. Use for: request counts, errors, completed tasks.

```python
from tiny_metrics import Counter, Gauge, Histogram, Summary

errors = Counter("http_errors", ["method", "status"])
errors.labels(method="GET", status="500").inc()
errors.labels(method="POST", status="200").inc()
print(errors.collect())
# {'http_errors': {'labels': {'method': 'GET', 'status': '500'}, 'value': 1}, ...}
```

### `Gauge`
瞬时值，可上下波动。用于：当前连接数、内存使用、队列深度。

```python
active = Gauge("active_connections", ["service"])
active.labels(service="api").set(42)
active.labels(service="api").dec(5)
```

### `Histogram`
观察值的分布桶。用于：延迟、响应大小。

```python
latency = Histogram("request_latency_seconds", ["endpoint"],
                    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0])
latency.labels(endpoint="/api/users").observe(0.073)
```

### `Summary`
分位数近似。用于：p50/p90/p99 延迟。

```python
duration = Summary("request_duration_seconds", ["route"])
with duration.labels(route="/home").time():
    do_work()
```

## Prometheus Exposition Format

```python
from tiny_metrics import generate_prometheus_output

# At /metrics endpoint
output = generate_prometheus_output()
# Returns Prometheus text exposition format string
```

## Push Gateway Support

```python
from tiny_metrics import push_to_gateway

push_to_gateway("localhost:9091", job="my_service", registry=registry)
```

## Last Verified

2026-08-08
