# /benchmark Command

## Trigger

User types: `/benchmark <function>`, `/benchmark compare`, or "How fast is this?"

## Description

Benchmarks code performance using stdlib timing tools. Measures wall time,
CPU time, and memory usage with statistical analysis.

## Usage

```
/benchmark <target> [--iterations=N] [--compare=<alt>] [--memory]
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `target` | Function or module to benchmark | Required |
| `--iterations` | Number of runs | 100 |
| `--warmup` | Warmup runs before timing | 10 |
| `--compare` | Alternative implementation to compare | None |
| `--memory` | Measure memory usage | False |
| `--input` | Test data or size specification | Default fixture |

## Workflow

1. **Resolve target** — find function/module in project
2. **Prepare input** — generate or load test data
3. **Warmup** — run target to prime caches
4. **Time runs** — execute N iterations, record `time.perf_counter()`
5. **Statistics** — compute mean, median, stdev, min, max
6. **Memory (optional)** — use `tracemalloc` for peak usage
7. **Compare (optional)** — run alternative, compute speedup ratio
8. **Report** — formatted table + conclusion

## Output Format

```
Benchmark: url_cleaner.normalize_url
Iterations: 100 | Warmup: 10

Timing Results
--------------
Mean:   1.234 ms
Median: 1.210 ms
Stdev:  0.089 ms
Min:    1.100 ms
Max:    1.560 ms

Memory (peak): 2.4 MB

Comparison: normalize_url_v2
------------------------------
Implementation    Mean (ms)    Speedup
normalize_url     1.234        baseline
normalize_url_v2  0.456        2.7x faster
```

## Example

**User:** `/benchmark normalize_url --iterations=1000 --memory`

**Result:**
```
Benchmark: normalize_url
Iterations: 1000 | Warmup: 10

Timing Results
--------------
Mean:   0.045 ms
Median: 0.043 ms
Stdev:  0.008 ms
Min:    0.038 ms
Max:    0.123 ms

Memory (peak): 0.8 MB

Result: Fast enough for batch processing (>20K URLs/sec)
```

## Notes

- Uses `benchmark-runner` skill for implementation
- No external dependencies (no `pytest-benchmark`, no `timeit` module needed)
- Automatically handles mutable input copying to avoid cache effects
- Reports in human-readable units (ms, μs, MB, GB)
