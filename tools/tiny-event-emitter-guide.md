# tiny-event-emitter Guide

**tiny-event-emitter** — Zero-dependency Node.js-style EventEmitter.

- **Repo:** github.com/hussain-alsaibai/tiny-event-emitter
- **Install:** `pip install tiny-event-emitter` or copy `tiny_event_emitter.py`
- **Size:** ~400 LOC, 0 dependencies
- **Tests:** 16 passing

## When to Use

When you need pub/sub to decouple components. Use instead of direct callbacks for async event systems, plugin architectures, and real-time notification pipelines.

## Quick Start

```python
from tiny_event_emitter import EventEmitter

emitter = EventEmitter()

@emitter.on("user:login")
def on_login(user_id):
    print(f"User {user_id} logged in")

emitter.once("startup", lambda: print("Started!"))
emitter.emit("user:login", user_id=42)

# Async listeners
async def on_data(data):
    await process(data)

emitter.on("data", on_data)
await emitter.emit_async("data", {"key": "value"})

# Wildcard patterns
emitter.on("user:*", lambda data: log(data))     # catches all user:* events
emitter.on("error.*", lambda data: alert(data))  # catches all error:* events
```

## Key Features

- Node.js EventEmitter API surface
- Async listeners with `emit_async()`
- Wildcard patterns: `*`, `user:*`, `error.*`
- Error handlers via `on_error()`
- Thread-safe `ThreadEventEmitter` variant
- Zero dependencies
