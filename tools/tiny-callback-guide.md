# tiny-callback Guide

## Repo
https://github.com/hussain-alsaibai/tiny-callback

## What It Does

Zero-dependency async callbacks, promise-style deferreds, and an event emitter for Python. One file, no setup.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_callback import
EventEmitter, Promise` and a `Promise()` object with `.then()` / `.catch()` /
`.resolve()`. **There is no `Promise` class.** Verified against upstream
`tiny_callback.py`:

```
__all__ = ['Callback', 'EventEmitter', 'deferred', 'emit', 'on', 'once']
```

Top-level names: `Callback`, `EventEmitter`, `deferred`, `emit`, `on`, `once`,
plus internal `_Deferred` and `_Handler`.

The promise-style object is **`deferred()`**, not `Promise`.

## When to Use

- **Async callback chaining** — register callbacks on async operations without third-party async libs
- **Promise/Deferred pattern** — represent pending async results as first-class objects
- **Event-driven architectures** — decouple components with event emission and subscription
- **Middleware systems** — register and compose async middleware layers

## Key patterns

```python
from tiny_callback import EventEmitter, deferred, on, emit, once

emitter = EventEmitter()

@emitter.on("data")
def handle_data(data):
    print(f"Got: {data}")

emitter.emit("data", {"key": "value"})
```

`deferred()` returns a pending-result object with a resolver, for the
promise/deferred pattern. `on()` and `once()` are module-level subscription
helpers; `once()` auto-unsubscribes after the first call.

## Related

- `tools/tiny-events-guide.md` — `tiny-events`, a different repo with an `EventBus`
- `tools/tiny-event-emitter-guide.md` — `tiny-event-emitter`, also distinct
- `tools/tiny-event-bus-guide.md` — durable pub/sub with replay
