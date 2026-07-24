# tiny-events — Zero-Dependency Event Emitter

## Repo
https://github.com/hussain-alsaibai/tiny-events

## What It Does

Zero-dependency event emitter for Python. One file, no setup. Pub/sub pattern for decoupling components.

## When to Use

- Decoupling modules in a larger application
- Plugin/extension systems
- Simple pub/sub without Redis or message queues

## Key Features

- `on(event, handler)` — subscribe
- `off(event, handler)` — unsubscribe
- `emit(event, *args, **kwargs)` — publish
- Wildcard subscriptions (`on("user:*")`)
- Once handlers (auto-unsubscribe after first call)
- Async event support

## Quick Start

```python
from tiny_events import EventEmitter

emitter = EventEmitter()

@emitter.on("build:complete")
def on_build_complete(result):
    print(f"Build done: {result}")

emitter.emit("build:complete", result={"status": "ok", "duration": 12.3})
```

## Last Verified
2026-07-23
