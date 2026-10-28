# tiny-llm-router — Zero-Dep Model Router with Cost & Latency Guards

> Zero-dependency model router for Python AI agents. Pick the right model per role — fast for chat, deep for think, vision-capable for images — with cost caps, latency guards, and circuit-breakers.
> Last verified: 2026-10-28 | Version 0.1.0 | hussain-alsaibai/tiny-llm-router
> **14/14 tests passing**, measured by run against the upstream clone. The
> package had **no CI** until 2026-10-28.

## The Build Failure (fixed 2026-10-28)

The package **could not be built at all**: the `pyproject.toml` used the key
`py_modules` (underscore) instead of `py-modules` (hyphen). setuptools ignores
the misspelled key, so the wheel shipped nothing.

```toml
py_modules = ["tiny_llm_router"]   # WRONG - silently ignored
py-modules = ["tiny_llm_router"]   # RIGHT
```

The PyPI name `tiny-llm-router` is **free** (verified 2026-10-28); the package
is not published there yet.

## What It Is

A single-file (~280 LOC) Python router that picks the right model per role with built-in cost caps, latency SLAs, fallback chains, and circuit-breakers. Stdlib only.

- Role-based rules: `code`, `think`, `vision`, `long`, `json`, `default`
- `max_cost_per_1k` cap per rule — refuse over-budget picks
- Latency `record()` after each call → rolling p95 enforcement
- Circuit-breaker after N errors → auto-route to fallback
- `pick(Task)` walks candidate list with per-rule filters (fixed `only_if` bug: now falls through instead of raising)
- 14/14 tests, 303K picks/sec, bench 3.3µs/pick
- MIT

## Why It Exists

The agent model landscape is no longer "pick one". Every serious agent today routes between 4–6 models:

| Model | Role | Why |
|-------|------|-----|
| `gpt-4o-mini` / `haiku` | fast chat | $0.15/M input, sub-second |
| `gpt-4o` | vision | best multimodal bang/buck |
| `o1-mini` / `nemotron-3` | think | heavy reasoning when it matters |
| `qwen3-coder` | code | code-specialized |
| `gemini-2.5-flash` | long context | 1M+ tokens, cheap |
| `kimi-k2.6` | default | free-tier, fast, decent |

The hard part is **the routing logic itself** — cost caps, latency SLAs, fallback chains, and breaking a flaky provider after N errors. `tiny-llm-router` ships all of that.

## Repo

https://github.com/hussain-alsaibai/tiny-llm-router

## When to Use

- You have 2+ models in production and want policy-driven routing
- You need a circuit-breaker for a flaky provider (rate limits, downtime)
- You want a cost guard per task type (think mode is expensive — cap it)
- You want one `pick()` call to handle `code`/`think`/`vision`/`default` without if/else trees

## Minimal Example

```python
from tiny_llm_router import Router, RoleRule, Task

router = Router([
    RoleRule("code",    "gpt-4o-mini", max_cost_per_1k=0.5),
    RoleRule("think",   "o1-mini"),
    RoleRule("vision",  "gpt-4o"),
    RoleRule("long",    "gemini-2.5-flash"),
    RoleRule("json",    "haiku"),
    RoleRule("default", "gpt-4o-mini"),
], fallback="haiku")

model = router.pick(Task(role="code", prompt="def hello(): return 1"))
print(model)   # gpt-4o-mini

# After each real call:
router.record(model, latency_ms=120, cost_usd=0.0023)
```

## Adapters

```python
# Drop-in for tiny-llm (existing transport layer):
router = make_tiny_llm_adapter(router, llm_module)
result = llm_module.chat_auto("summarize this thread")
```

## Tested Patterns

- Cost-cap walk: when no rule fits budget, falls through to fallback
- Latency p95 enforcement: blocks role if 3-of-5 last calls exceed SLA
- Circuit-breaker: after 5 errors in 60s on `gpt-4o`, auto-route to `haiku`
- `only_if` filters evaluated in order; first match wins; missing match → next rule (does NOT raise)

## See Also

- `tools/tiny-trace-otel-guide.md` — pair for per-call spans
- `tools/tiny-budget-ledger-guide.md` — pair for hard spend caps
