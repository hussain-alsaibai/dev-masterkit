# tiny-agent-scope

> **Resource budgets and blast-radius limits for AI agents.** Cap steps, tool calls, tokens, cost, wall time; allow/deny tools, paths, and hosts. Raise on violation, or hook it to a kill switch. Zero deps, single file, MIT.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](#)
[![Zero deps](https://img.shields.io/badge/dependencies-zero-success.svg)](#)
[![Tests](https://img.shields.io/badge/tests-32%20passing-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Why?

By 2026 the agent that *runs* is the one you actually have to constrain. Three failure modes are everywhere:

1. **Cost runaway** — agent loops on a flaky API, burns $14 overnight
2. **Tool sprawl** — model invents a new tool name and your logger gets confused
3. **Path / host escape** — agent reads `~/.ssh/id_rsa` or POSTs to `evilcorp.io`

`tiny-agent-scope` is the small guardrail that wraps any agent loop:

```python
from tiny_agent_scope import scope_for, BudgetExceeded, ScopeViolation

scope = scope_for(
    "research-agent",
    max_steps=20,
    max_tool_calls=50,
    max_tokens=200_000,
    max_cost_usd=2.00,
    max_wall_seconds=300,
    allowed_tools={"search", "read_file", "summarize"},
    denied_tools={"exec", "write_file", "delete"},
    allowed_paths=["./workspace/*"],
    allowed_hosts={"api.example.com", "*.wikipedia.org"},
    on_violation=lambda s, k, t: alert(f"agent {s.name}: {k} -> {t}"),
)

try:
    while not scope.aborted():
        scope.step()
        result = run_tool(call.name, call.args)
        scope.record_tool_call(call.name, tokens=result.tokens, cost_usd=result.cost)
        if scope.remaining()["cost_usd"] is not None and scope.remaining()["cost_usd"] < 0.05:
            scope.abort()  # graceful stop
except BudgetExceeded as e:
    print(f"halt: {e}")
except ScopeViolation as e:
    print(f"refused: {e}")
finally:
    print(scope.used())
```

## Features

- **Budgets** — `max_steps`, `max_tool_calls`, `max_tokens`, `max_cost_usd`, `max_wall_seconds`
- **Tool policy** — `allowed_tools`, `denied_tools`, `read_only_tools`
- **Filesystem policy** — `allowed_paths` (glob), `denied_paths`, write-block on read-only paths
- **Network policy** — `allowed_hosts`, `denied_hosts` (glob on host)
- **Live accounting** — `scope.used()` / `scope.remaining()` return real-time state
- **Callbacks** — `on_step`, `on_violation`, `on_abort` for observability + kill switch
- **Graceful abort** — `scope.abort()` sets a flag; the next `step()` raises `BudgetExceeded`
- **Zero dependencies** — pure stdlib, ~280 LOC, 32/32 tests passing
- **Context manager** — `with agent_scope(...):`

## API

### `AgentScope` / `scope_for(name, **kwargs)`
| Parameter | Type | Description |
|-----------|------|-------------|
| `max_steps` | int | Hard cap on agent loop iterations |
| `max_tool_calls` | int | Hard cap on tool invocations |
| `max_tokens` | int | Hard cap on total tokens consumed |
| `max_cost_usd` | float | Hard cap on accumulated cost |
| `max_wall_seconds` | float | Hard cap on wall-clock time |
| `allowed_tools` | set | Whitelist (None = all) |
| `denied_tools` | set | Blacklist (checked first) |
| `read_only_tools` | set | Paths declared read-only |
| `allowed_paths` | list | Glob patterns (None = all) |
| `denied_paths` | list | Glob patterns (checked first) |
| `allowed_hosts` | list | Glob patterns (None = all) |
| `denied_hosts` | list | Glob patterns (checked first) |
| `on_step` | callable | `(scope, step_name) -> None` |
| `on_violation` | callable | `(scope, kind, target) -> None` |
| `on_abort` | callable | `(scope) -> None` |

### Methods
- `scope.step(name="")` — increment step counter, check budgets
- `scope.record_tool_call(name, tokens=0, cost_usd=0.0)` — increment + check
- `scope.record_tokens(n)` / `scope.record_cost(usd)`
- `scope.check_path(path, write=False)` — raise on violation
- `scope.check_url(url)` — raise on violation
- `scope.abort()` / `scope.aborted()`
- `scope.used()` / `scope.remaining()` — dicts

### Exceptions
- `BudgetExceeded(budget, used, limit)` — `scope.step` raises this on overrun
- `ScopeViolation(kind, target)` — `check_path` / `check_url` / denied tools raise this

## Integration

```python
# tiny-cost interop
from tiny_cost import track
from tiny_agent_scope import scope_for

scope = scope_for("agent", max_cost_usd=1.00)

@track(scope=scope)
def call_openai(prompt):
    return openai.chat.completions.create(...)

# tiny-trace interop
from tiny_trace_otel import get_tracer
tracer = get_tracer()
with tracer.start_span("agent.run") as span:
    span.set_attribute("scope.used", str(scope.used()))
```

## Why "tiny"?

Part of the OpenClaw zero-dep, single-file ecosystem: `tiny-llm`, `tiny-llm-router`, `tiny-tool-result`, `tiny-semantic-cache`, `tiny-cost`, `tiny-trace`, `tiny-trace-otel`, `tiny-event-bus`, `tiny-router`, `tiny-config`, `tiny-log`, `tiny-validator`, `tiny-cli`, `tiny-rate-limiter`, `tiny-circuit-breaker`, `tiny-retry-plus`, `tiny-workflow-engine`, `tiny-scheduler`, and 50+ more.

## License

MIT — copy-paste, modify, ship.
