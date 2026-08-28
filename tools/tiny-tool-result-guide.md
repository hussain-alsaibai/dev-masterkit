# tiny-tool-result — Structured Success/Failure Envelopes for Agent Tool Calls

**Repository:** https://github.com/hussain-alsaibai/tiny-tool-result
**Last verified:** 2026-08-28
**License:** MIT
**Dependencies:** Zero (Python stdlib only)

## What it does

A lightweight `@wrap` decorator that wraps any tool/function call and returns a structured `ToolResult` envelope with success/failure status, typed data or error, timing, and retry metadata. Designed for AI agent pipelines that need consistent, introspectable tool call results.

## When to use

Use in any AI agent or workflow engine where tool calls need consistent error handling, retry awareness, timing metrics, and structured output — without adding a heavy framework dependency.

## Quick start

```python
from tiny_tool_result import wrap, ToolStatus

@wrap
def call_api(url: str) -> dict:
    import urllib.request
    with urllib.request.urlopen(url) as r:
        return {"status": r.status, "body": r.read()}

result = call_api("https://api.example.com/data")
print(result.status)       # ToolStatus.SUCCESS or ToolStatus.FAILURE
print(result.data)         # parsed return value or None
print(result.error)        # exception message or None
print(result.elapsed_ms)   # call duration in ms
print(result.attempts)     # number of attempts (1 if no retry)
```

## ToolResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | `ToolStatus` | SUCCESS, FAILURE, RETRY, TIMEOUT |
| `data` | `Any` | Return value on success |
| `error` | `str` | Error message on failure |
| `elapsed_ms` | `float` | Wall-clock time in milliseconds |
| `attempts` | `int` | Number of attempts made |
| `tool_name` | `str` | Name of the wrapped function |

## Retry-Aware Wrapping

```python
@wrap(max_attempts=3, retry_on=(ConnectionError, TimeoutError))
def unreliable_call():
    ...
```

The decorator records `ToolStatus.RETRY` internally and increments `attempts` on each try, returning `ToolStatus.SUCCESS` if the final attempt succeeds or `ToolStatus.FAILURE` if all fail.

## Timeout Enforcement

```python
@wrap(timeout_ms=5000)
def slow_operation():
    ...
```

Returns `ToolStatus.TIMEOUT` if the call exceeds the deadline.

## Batch Tool Results

```python
results = [
    call_api("https://api1.example.com"),
    call_api("https://api2.example.com"),
]

for r in results:
    if r.status == ToolStatus.FAILURE:
        print(f"Failed: {r.error}")
```

## Usage in Agent Workflows

```python
# Agent pipeline can inspect every tool result uniformly
for tool_name, args in plan.steps:
    result = registry.call(tool_name, args)
    if result.status != ToolStatus.SUCCESS:
        workflow.handle_failure(result)
    elif result.elapsed_ms > 1000:
        log.warning(f"{tool_name} slow: {result.elapsed_ms}ms")
```

## Tests

Cover: success path, exception propagation, timeout, retry count, field population, and batch usage.

## Last Verified: 2026-08-28

- Repo: `hussain-alsaibai/tiny-tool-result`
- Version: v0.1.0
- Verification: `python -m pytest` — all tests pass
