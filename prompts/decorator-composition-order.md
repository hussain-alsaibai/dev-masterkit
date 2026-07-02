# decorator-composition-order — Prompt for stacked-decorator correctness

## Description

When you stack decorators with a meta-helper (`@composed(a, b, c)`,
`@stack([a, b, c])`) or build a decorator-stacking utility, the order you
apply the factories determines what actually runs first. Use this prompt to
make the choice explicit and tested.

## When to use

- Writing a `composed` / `stack` / `chain` meta-decorator
- Debugging why a wrapped function logs/rets in the wrong order
- Reviewing a PR that adds decorator-stacking helpers

## The prompt

```
We are building a meta-decorator: @composed(a, b, c) on a function `core`.

Semantics we want:
  - composed(a, b, c) is exactly equivalent to:
        @a
        @b
        @c
        def core(): ...
  - That means the runtime order is: a(core) first, then b wraps that, then c wraps THAT.
  - The function actually called first (the outermost) is `a`; the innermost (closest to core) is `c`.

Implementation rules:
  1. Apply factories in REVERSED order over the inner function:
        f = core
        for fac in reversed(factories):
            f = fac(f)
  2. Record the resulting chain so a `peek(fn)` helper can report it OUTER-FIRST.
        chain_reversed = list(factories)        # [a, b, c]
        chain_outer_first = list(reversed(chain_reversed))  # [c, b, a] as applied
     If you display, reverse again to show outer-first: [a, b, c].
  3. For each factory, set `deco.__name__ = factory.__name__` so introspection
     isn't shadowed by the inner `def deco(fn):` closure.
  4. Tests MUST cover:
        - the OUTER call enters first (a runs before b before c)
        - the return value unwraps in REVERSE (c's result → b → a)
        - the order survives asyncio (decorator is coroutine-aware)

DO NOT:
  - Use `functools.partial(factory, arg)` as if it were a wrapped decorator.
    `partial(add_n_factory, 3)` returns the inner `deco`, not a wrapper.
    Use `partial(some_decorator, n=3)` only when the decorator signature is `(fn, n=...)`.
```

## Why this exists

The first implementation of `tiny-compose.composed` applied factories in
forward order, producing `[b][a]core[/a][/b]` instead of the expected
`[a][b]core[/b][/a]`. The fix was two lines (`reversed(...)` + display
re-reversal) plus the `__name__` patch. Tests now lock both the call order
and the return-unwind order.

Last verified: 2026-07-02
