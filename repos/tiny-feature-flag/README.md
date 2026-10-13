# tiny-feature-flag

> Zero-dependency feature flag / toggle evaluation.

A small library for evaluating feature flags at request time.  Flags
are defined as `Flag` objects with a default state, a list of rules,
and a set of overrides.  Each rule is a callable that takes a
`Context` and returns `True`, `False`, or `None` (defer).

## Install

```bash
pip install tiny-feature-flag
```

## Quick start

```python
from tiny_feature_flag import Flag, Rule, Context, FlagStore

dark_mode = Flag(
    name="dark_mode",
    default=False,
    rules=[
        Rule.matches(lambda v: v == "pro", "user.plan"),
        Rule.percent("user.id", 20, salt="dark_mode"),
    ],
)

store = FlagStore({"dark_mode": dark_mode})

if store.enabled("dark_mode", Context(user={"plan": "pro", "id": "u1"})):
    render_dark_ui()

# 20% rollout to free users with stable hash on user.id
if store.enabled("dark_mode", Context(user={"plan": "free", "id": "u2"})):
    render_dark_ui()
```

## Rule semantics

Each rule returns one of three values:

- `True` -> the flag is **enabled** for this context.
- `False` -> the flag is **forced off** (next rule is *not* tried).
- `None` -> no opinion; **defer** to the next rule (or the flag default).

This three-valued return is what makes tiered rollouts work:

```python
# Pro users always; otherwise 20% of free users
Flag(name="x", default=False, rules=[
    Rule.matches(lambda v: v == "pro", "user.plan"),  # defer on non-pro
    Rule.percent("user.id", 20, salt="x"),  # defer on out-of-bucket
])
```

Use `Rule.eq` (force off on mismatch) when you want a hard rule
that explicitly excludes a segment.

## Built-in rules

- `Rule.eq(path, value)` -> True if `ctx.get(path) == value`, else False.
- `Rule.ne(path, value)` -> True if `ctx.get(path) != value`, else False.
- `Rule.in_(path, values)` -> True if `ctx.get(path) in values`, else False.
- `Rule.contains(path, needle)` -> True if `needle in ctx.get(path)`, else False.
- `Rule.matches(predicate, path)` -> True if predicate matches, else defer.
- `Rule.percent(path, percent, *, salt="")` -> stable percentage rollout.
- `Rule.predicate(fn)` -> wrap a `Context -> bool` function.

## Context

`Context` holds the per-request data:

```python
ctx = Context(
    user={"id": "u1", "plan": "pro", "roles": ["admin"]},
    request={"path": "/checkout"},
    env={"region": "us"},
    extra={"trace_id": "abc"},
)
ctx.get("user.plan")  # "pro"
ctx.get("env.region")  # "us"
ctx.get("missing", "default")  # "default"
```

## Overrides

Force a flag on or off for a specific user / request:

```python
flag = Flag(name="v2_endpoint", default=False)
flag.add_override("user.id", "ops-alice", True)  # ops-alice always sees v2
flag.add_override("user.id", "blocked-user", False)  # blocked-user never sees it
```

Overrides are evaluated *before* rules.  The first matching override
wins; if none match, the rule chain runs as usual.

## /debug/flags

Use `FlagStore.evaluate_all(ctx)` to dump every flag at once:

```python
return store.evaluate_all(ctx)  # {"dark_mode": True, "v2_endpoint": False, ...}
```

## License

MIT
