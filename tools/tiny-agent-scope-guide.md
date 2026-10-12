# tiny-agent-scope Guide

> Resource budgets and blast-radius limits for AI agents. ~280 LOC, 32 tests, stdlib-only.

**Repo:** `github.com/hussain-alsaibai/tiny-agent-scope`
**Version:** 0.1.0 (2026-10-10)
**Author:** OpenClaw (autonomous cron, daily-bounty-workflow context)
**Status:** ✅ Initial release — 32/32 tests passing. Zero runtime deps.

---

## What is it?

`tiny-agent-scope` is a single-file Python library (~280 LOC) that wraps any agent loop with five budgets (steps, tool calls, tokens, cost, wall time), three allow/deny lists (tools, paths, hosts), callbacks for observability, and a graceful `abort()` kill switch.

It is the guardrail layer for the 2026 Q4 "agent is a stack" pattern. See the [Developer Tools Landscape 2026-10-10](../../dev-reports/2026-10-10-developer-tool-trends.md) report (Pattern 2: "the scope pattern") for the cross-ecosystem context.

## Why does it exist?

By 2026 the agent that *runs* is the one you actually have to constrain. Three failure modes are everywhere:

1. **Cost runaway** — agent loops on a flaky API, burns $14 overnight
2. **Tool sprawl** — model invents a new tool name and your logger gets confused
3. **Path / host escape** — agent reads `~/.ssh/id_rsa` or POSTs to `evilcorp.io`

`tiny-agent-scope` is the small guardrail that wraps any agent loop and turns the "should this have happened?" question into a single, testable Python object.

## Usage

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

### Context manager

```python
from tiny_agent_scope import agent_scope

with agent_scope("daily-bounty", max_cost_usd=0.50, max_wall_seconds=600) as scope:
    while not scope.aborted():
        scope.step()
        ...
```

## API Reference

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

- `scope.step(name="")` — increment step counter, check budgets (raises on overrun)
- `scope.record_tool_call(name, tokens=0, cost_usd=0.0)` — increment + check
- `scope.record_tokens(n)` / `scope.record_cost(usd)` — accounting
- `scope.check_path(path, write=False)` — raise on violation
- `scope.check_url(url)` — raise on violation
- `scope.abort()` / `scope.aborted()`
- `scope.used()` / `scope.remaining()` — dicts with live state

### Exceptions

- `BudgetExceeded(budget, used, limit)` — `scope.step` raises this on overrun
- `ScopeViolation(kind, target)` — `check_path` / `check_url` / denied tools raise this

## Policy precedence

For each kind of check, the order is:
1. `denied_*` list — matches raise `ScopeViolation`
2. `allowed_*` list — if set, only matches are permitted
3. Otherwise — allow

This means `denied_tools={"exec"}` always wins over `allowed_tools={"*"}`.

## Cross-Repo Interop

`tiny-agent-scope` is part of the **OpenClaw developer tools ecosystem**:

- **tiny-cost** — `@track(scope=scope)` decorator feeds `record_cost_usd`
- **tiny-rate-limiter** — per-tool-call rate policy; scope adds the *total* cap
- **tiny-circuit-breaker** — failure-rate gating; scope adds the *budget* cap
- **tiny-retry-plus** — retry policy; scope is the *outer* kill switch
- **tiny-tool-result** — the `tool` field on `ToolResult` maps to `record_tool_call`
- **tiny-trace-otel** — `scope.used()` can be set as a span attribute on each step
- **dev-masterkit** — the curated collection; this guide lives there

## Adoption Path

1. `pip install tiny-agent-scope`
2. Wrap your agent loop: `scope = scope_for(name, max_cost_usd=..., max_wall_seconds=...)`
3. Replace `if cost > 1.0: break` with `if scope.remaining()["cost_usd"] < 0.05: scope.abort()`
4. Add `allowed_tools=` and `denied_tools=` per agent role
5. Add `on_violation=` to feed the alert channel
6. Wire `scope.used()` into your trace spans
7. In CI, run a fuzz test that exercises every deny path

## Roadmap (next 7 days)

- `tiny-agent-scope` v0.1.1 — bug-fix release if any zero-dep issues surface
- `tiny-agent-scope` v0.2.0 — adds `nested_scope()` for sub-agent budget isolation
- `tiny-llm-router` — `role` presets will read from `scope` for cost-aware routing
- `dev-masterkit` — adopt as the standard wrapper for all cron-triggered agents

## See also

- [dev-reports/2026-10-10-developer-tool-trends.md](../../dev-reports/2026-10-10-developer-tool-trends.md) — "The scope pattern" (Pattern 2)
- [tiny-tool-result-guide.md](./tiny-tool-result-guide.md) — uniform envelope that every scoped call returns
- [tiny-skill-loader-guide.md](./tiny-skill-loader-guide.md) — plugin loader; pair with `allowed_tools` for the loaded skills
- [MEMORY.md](../../MEMORY.md) — Tiny-* stack overview (50+ repos)
