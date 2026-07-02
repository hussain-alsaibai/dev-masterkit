# tiny-compose — Zero-Dependency Decorator Stacker

## Repo
https://github.com/hussain-alsaibai/tiny-compose

## One-liner
Meta-decorator stacker: `composed(a, b, c)`, `stack([...])`, `pipeline(f, g, h)`.
Sync + async auto-detect, `use()` / `set_layer()` global layer, `peek()` / `remove()` introspection.

## Install
```bash
pip install tiny-compose
```

## Quick Example

```python
from tiny_compose import composed, pipeline, use, set_layer

@composed(timed, cached(ttl=60), retry(times=3))
def fetch(url):
    return requests.get(url).json()

# Or sequential pipeline
@pipeline(validate, transform, persist)
def ingest(record):
    ...

# Global middleware layer
set_layer(log_calls, auth_check)
@use
def handler(req): ...
```

## Patterns

- **Composition order:** `composed(a, b, c)` applies right-to-left (c first, then b, then a) — matches stacked `@a @b @c` semantics.
- **Pipeline order:** `pipeline(f, g, h)` runs top-to-bottom (f, then g, then h) — reads as a recipe.
- **Async-aware:** detects `iscoroutinefunction(fn)` and returns an async wrapper; no separate `@acomposed` needed.
- **Global layer:** `set_layer(...)` registers cross-cutting concerns; `use` decorates every subsequent function in the module.

## API

| Helper | Purpose |
|--------|---------|
| `composed(*facs)` | Stack decorators (right-to-left) |
| `stack(facs)` | Alias for `composed` |
| `pipeline(*facs)` | Sequential execution (left-to-right) |
| `use(fn)` | Apply current global layer to `fn` |
| `set_layer(*facs)` | Set the global layer |
| `add_layer(*facs)` | Append to the global layer |
| `peek(fn)` | Inspect decorator chain on a function |
| `remove(fn, name)` | Strip a decorator by registered name |

## Testing

- **53/53 tests passing**
- 411 LOC + 598 test LOC
- 0 dependencies, 0 transitive deps
- Decorator ordering, async routing, global layer reset, peek/remove — all covered

## Gotcha — functools.partial of a factory

```python
# This does NOT work the way you'd hope:
add_3 = partial(add_n_factory, 3)  # returns inner deco closure, NOT a wrapper

# This works:
@partial(some_decorator, n=3)     # binds the kwarg on the decorator itself
def f(): ...
```

Use the second form. The first form isn't supported.

Last verified: 2026-07-02
