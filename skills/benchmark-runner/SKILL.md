# benchmark-runner — Skill for Performance Benchmarking

## Trigger

Use when the user asks to:
- "Benchmark this code"
- "How fast is [function]?"
- "Performance test"
- "Compare implementations"
- "Profile my code"
- "Find bottlenecks"

## Description

Measures and compares code performance using only Python's standard library.
Produces reproducible, statistically meaningful results with no external
dependencies.

## Procedure

### 1. Define Benchmark Scope

Identify:
- Target function(s) or code blocks
- Input sizes/data to test
- What to measure: wall time, CPU time, memory, throughput
- Comparison baseline (previous version, alternative implementation)

### 2. Choose Measurement Method

| Metric | Standard Library Tool |
|--------|----------------------|
| Wall time | `time.perf_counter()` |
| CPU time | `time.process_time()` |
| Memory | `tracemalloc` (3.4+) |
| Function call count | `sys.setprofile` or manual counting |

### 3. Write Benchmark Harness

```python
import time
import statistics
from functools import wraps

def benchmark(func, args, iterations=100, warmup=10):
    """Run func(*args) multiple times and return statistics."""
    # Warmup
    for _ in range(warmup):
        func(*args)

    # Timed runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "total": sum(times),
        "iterations": iterations,
        "result_sample": result,  # Last result
    }
```

### 4. Compare Implementations

```python
def compare(algorithms, test_data, iterations=100):
    """Compare multiple implementations."""
    results = {}
    for name, func in algorithms.items():
        stats = benchmark(func, (test_data,), iterations=iterations)
        results[name] = stats

    # Print comparison table
    print(f"{'Algorithm':<20} {'Mean (ms)':<12} {'Median':<12} {'Stdev':<12}")
    print("-" * 56)
    for name, stats in sorted(results.items(), key=lambda x: x[1]["mean"]):
        print(f"{name:<20} {stats['mean']*1000:<12.4f} {stats['median']*1000:<12.4f} {stats['stdev']*1000:<12.4f}")

    return results
```

### 5. Memory Profiling with tracemalloc

```python
import tracemalloc

def benchmark_memory(func, args):
    tracemalloc.start()
    tracemalloc.reset_peak()

    result = func(*args)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "current_bytes": current,
        "peak_bytes": peak,
        "current_mb": current / 1024 / 1024,
        "peak_mb": peak / 1024 / 1024,
    }
```

### 6. Generate Benchmark Report

```markdown
# Benchmark Report

## Test Environment
- Python: {version}
- Platform: {platform}
- CPU: {cpu_info}
- Date: {timestamp}

## Results

### {Function Name}

| Metric | Value |
|--------|-------|
| Iterations | {N} |
| Mean | {X} ms |
| Median | {X} ms |
| Std Dev | {X} ms |
| Min | {X} ms |
| Max | {X} ms |
| Total | {X} s |

### Comparison

{best_algorithm} is {speedup}x faster than {worst_algorithm}.

## Conclusion

{recommendation}
```

## Example

**User:** "Benchmark sorting 10,000 random integers."

**Generated benchmark:**
```python
import random
import statistics
import time

def benchmark_sort(algorithms, n=10_000, iterations=50):
    data = [random.randint(0, 1_000_000) for _ in range(n)]
    results = {}

    for name, sort_func in algorithms.items():
        times = []
        for _ in range(iterations):
            test_data = data.copy()
            start = time.perf_counter()
            sort_func(test_data)
            times.append(time.perf_counter() - start)

        results[name] = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times),
        }

    return results

# Usage
algorithms = {
    "Timsort (builtin)": sorted,
    "Bubble sort": lambda x: bubble_sort(x),
}
results = benchmark_sort(algorithms)
```

**Output:**
```
Algorithm            Mean (ms)    Median       Stdev
--------------------------------------------------------
Timsort (builtin)    1.2345       1.2100       0.0890
Bubble sort          4523.0000    4510.0000    45.0000

Timsort is 3665x faster than Bubble sort.
```

## Validation Checklist

- [ ] Benchmark uses sufficient iterations (> 30) for statistical significance
- [ ] Warmup runs performed before timing
- [ ] Input data is representative of real usage
- [ ] Results include mean, median, and standard deviation
- [ ] Multiple implementations compared if applicable
- [ ] Memory usage measured for memory-bound operations
- [ ] Environment documented (Python version, platform)
- [ ] Results are reproducible (fixed seeds where randomness used)
- [ ] No external benchmarking libraries used (timeit is acceptable but prefer explicit control)

## Notes

- Use `time.perf_counter()` not `time.time()` — it's monotonic and higher precision
- Run benchmarks on idle systems; background processes skew results
- For micro-benchmarks, Python overhead dominates — focus on algorithmic differences
- `timeit` module is acceptable but less flexible than manual timing
- Always copy mutable data before each run to avoid cache effects
- Report relative differences, not absolute times ("2x faster" is more meaningful than "10ms faster")
