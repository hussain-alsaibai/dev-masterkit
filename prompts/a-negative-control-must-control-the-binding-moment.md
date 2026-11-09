# A negative control must control the moment the value is bound

**Added:** 2026-11-09
**Last verified:** 2026-11-09 (reproduced against `tiny-route-redact` 0.2.0, fresh clone of `main`)
**Class:** verification / test design
**Cost of not knowing:** a false "fails open" finding sent to a published library

## The claim under test

`tiny-route-redact` 0.2.0 made a deliberate breaking change: when `tiny_secret_mask` is not
importable, `redact_path()` raises `RedactionUnavailable` instead of returning the path
unchanged. The release note says "fails closed."

Verifying a fail-closed claim requires making the dependency absent and observing the
behaviour. That is a negative control, and it is the only evidence that the guard works.

## The control I wrote first — and what it said

```python
import tiny_route_redact as t
import builtins
real = builtins.__import__
def fake(name, *a, **k):
    if name.startswith('tiny_secret_mask'):
        raise ImportError('hidden')
    return real(name, *a, **k)
builtins.__import__ = fake
print(t.redact_path("/x"))     # -> "/x"   ...  "FAIL OPEN"
```

The result was `/x`, unredacted, with no exception. Read at face value: the library's
headline safety property was false, on `main`, in a published repo. That is precisely the
kind of finding worth reporting.

It was wrong.

## Why it lied

The module binds the dependency once, at import:

```python
_MASK = _resolve_mask()          # module scope, runs once

def redact_path(path):
    if _MASK is None:
        raise RedactionUnavailable(...)
    return _MASK(path)
```

By the time the test patched `__import__`, `import tiny_route_redact` had already run
`_resolve_mask()` and bound a real `mask_route_path` into `_MASK`. The patch changed how
*new* imports resolve and had no effect on the value already captured.

**The control failed to control anything.** It intercepted the lookup path, not the
binding moment — and for a module-level constant, the binding moment is the only moment
that exists.

## The control that works

Seal the import *before* the module under test loads, with a `sys.meta_path` finder that
raises for the dependency name:

```python
import sys, importlib.abc

class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name.startswith('tiny_secret_mask'):
            raise ImportError('sealed')
        return None

sys.meta_path.insert(0, Block())
sys.path.insert(0, '/path/to/repo')
import tiny_route_redact as t         # first load, dependency already absent
```

Results, 2026-11-09:

| call | result |
|---|---|
| `redact_path("/x")` | raises `RedactionUnavailable` |
| `redact_path_passthrough("/x")` | returns `/x` |
| `route_redactor_middleware(fn)` | raises `RedactionUnavailable` |
| `route_redactor_asgi_middleware(fn)` | raises `RedactionUnavailable` |

The claim holds. `_MASK` is `None`, every guarded entry point refuses, and the only path
that returns unredacted input is the one whose name says so.

## The rule

> **A negative control must control the moment the value is bound, not the moment it is
> used.** If the code captures the dependency in a module-level constant, the control has
> to be installed before the module is first imported — otherwise it tests the interpreter,
> not the library.

## Recognising this shape

Any of these means the control must run before import:

- `_X = _resolve_x()` or `_X = some_import()` at module scope
- a module-level `try: import dep / except ImportError: dep = None`
- a singleton, a cached client, a configured logger, a plugin registry populated at import
- a decorator applied at class definition time

A `sys.modules` injection is also valid and often simpler:

```python
sys.modules['tiny_secret_mask'] = None      # import of this name now raises ImportError
```

`None` in `sys.modules` makes the next import raise `ModuleNotFoundError`, which is a
subclass of `ImportError` — the same branch the real absence takes.

## Two traps worth naming

**1. "It ran and printed something" is not a passing control.** My first control executed
cleanly, produced a plausible value, and was still meaningless. A control that cannot fail
is not a control; a control that fails for the wrong reason is worse, because it produces a
confident false accusation.

**2. Do not "fix" the library to satisfy the bad control.** The natural next move after
seeing "FAIL OPEN" is to move `_MASK` inside the function so late binding makes the test
pass. That changes working code for no user benefit. The correct conclusion here was that
the *test* was lying, and the artifact to throw away was the test.

## Check before reporting a fail-open finding

1. Where is the dependency bound — module scope or call time?
2. Did the control run before that line executed?
3. Does the control reproduce the *exact* failure the guard is written against (missing
   module), not a proxy (a patched import hook)?
4. Re-run it against the tagged release, not just a working tree.
5. If it still fails: state the version, the commit, and the reproducer verbatim.
