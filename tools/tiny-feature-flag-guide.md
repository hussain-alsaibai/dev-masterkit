# tiny-feature-flag Guide

> Zero-dependency feature flag / toggle evaluation. ~290 LOC, 28 tests, stdlib-only.

**Repo:** github.com/hussain-alsaibai/tiny-feature-flag
**Version:** 0.1.0 (2026-10-13)
**Author:** OpenClaw (autonomous cron, developer-tool-reports context)
**Status:** ✅ Initial release — 28/28 tests passing; three-valued rule semantics (True / False / None defer) is the differentiator.

---

## What is it?

`tiny-feature-flag` is a single-file Python library (~290 LOC) for evaluating feature flags at request time. Flags are `Flag` objects with a default state, a list of rules, and a set of overrides. Each rule returns `True` (enable), `False` (force off), or `None` (defer to the next rule).

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
```

## Why does it exist?

Most feature-flag libraries collapse the rule result to a boolean. The boolean trap loses the ability to express "tier A always, otherwise tier B partially" — you end up with nested conditionals or two separate flags. The three-valued return (True / False / None) makes tiered rollouts a flat rule list.

```python
# Pro users always; otherwise 20% of free users
Flag(name="x", default=False, rules=[
    Rule.matches(lambda v: v == "pro", "user.plan"),  # defer on non-pro
    Rule.percent("user.id", 20, salt="x"),            # defer on out-of-bucket
])
```

The defer semantics is the entire reason a flag has a list of rules and not a single predicate.

## Built-in rules

| Rule | Returns | Use for |
|------|---------|---------|
| `Rule.eq(path, value)` | True / False | "user.plan == 'pro'" (hard rule) |
| `Rule.ne(path, value)` | True / False | "user.plan != 'free'" (hard rule) |
| `Rule.in_(path, values)` | True / False | "user.region in {'us', 'ca'}" |
| `Rule.contains(path, needle)` | True / False | "'admin' in user.roles" |
| `Rule.matches(predicate, path)` | True / None | Defer on non-match (for layered rollouts) |
| `Rule.percent(path, percent, *, salt="")` | True / None | Stable percentage rollout |
| `Rule.predicate(fn)` | True / False | Wrap a `Context -> bool` function |

The pattern: `eq` / `ne` / `in_` / `contains` / `predicate` return False on mismatch (hard rule). `matches` / `percent` return None on mismatch (defer). Choose the hard ones when you want to *exclude* a segment; choose the defer ones when you want to *try the next rule*.

## Context

`Context` holds the per-request data:

```python
ctx = Context(
    user={"id": "u1", "plan": "pro", "roles": ["admin"]},
    request={"path": "/checkout"},
    env={"region": "us"},
    extra={"trace_id": "abc"},
)
ctx.get("user.plan")    # "pro"
ctx.get("env.region")   # "us"
ctx.get("missing", "default")  # "default"
```

## Overrides

Force a flag on or off for a specific user / request:

```python
flag = Flag(name="v2_endpoint", default=False)
flag.add_override("user.id", "ops-alice", True)   # ops-alice always sees v2
flag.add_override("user.id", "blocked-user", False) # blocked-user never sees it
```

Overrides are evaluated *before* rules. The first matching override wins; if none match, the rule chain runs as usual.

## Stable percentage rollouts

`Rule.percent("user.id", 20, salt="dark_mode")` uses SHA-256 bucketing. The same `(value, salt)` pair always lands in the same bucket, so rollouts are reproducible across restarts. Don't change the salt mid-rollout — it reshuffles every user.

## /debug/flags

```python
return store.evaluate_all(ctx)  # {"dark_mode": True, "v2_endpoint": False, ...}
```

Useful for an admin endpoint that shows what each user is seeing.

## When to use it

✅ Use `tiny-feature-flag` when:

- You have tiered rollouts (pro always, free partial) and want them as a flat rule list.
- You want stable percentage rollouts without external services.
- You want a single in-process flag store with no network hop.

❌ Don't use it when:

- You need cross-process flag changes (no remote config; reload means restart).
- You need audit logs of who-changed-what-when (no built-in audit trail).
- You need a UI for non-engineers to flip flags.

## License

MIT. Single file, zero dependencies.

**Last verified:** 2026-10-13
