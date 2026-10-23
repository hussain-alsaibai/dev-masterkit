# tiny-events — Zero-Dependency Event Bus

## Repo
https://github.com/hussain-alsaibai/tiny-events

## What It Does

Zero-dependency event bus for Python. One file, no setup. Pub/sub pattern for
decoupling components, with priority ordering and bounded history.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented an `EventEmitter` class with
`on()` / `off()` / `emit()` methods and a module-level `EventEmitter` import.
**That is not the shipped API.** Verified against upstream `tiny_events.py`:

```
__all__ = ['EventBus', 'Event', 'Priority', 'subscribe', 'emit']
```

Top-level names: `EventBus`, `Event`, `Priority`, `subscribe`, `emit`, `once`,
`wait_for`.

The correct import is:

```python
from tiny_events import EventBus, Event, Priority, subscribe, emit, once, wait_for
```

## Key Features

- `EventBus(max_history=100)` — bounded history, oldest entries evicted
- `subscribe` / `emit` / `once` — subscription and publication
- `wait_for` — await an event by name with a timeout
- `Priority` — ordered dispatch (high priority first)
- `Event` — the published record

## Quick Start

```python
from tiny_events import EventBus

bus = EventBus(max_history=100)

def on_complete(result):
    print(f"Build done: {result}")

bus.subscribe("build:complete", on_complete)
bus.emit("build:complete", result={"status": "ok", "duration": 12.3})
```

## When to Use

- Decoupling modules in a larger application
- Plugin/extension systems
- Simple pub/sub without Redis or message queues
- AI agent tool pipelines where a late subscriber needs to replay recent events
  (the bounded `max_history` covers this)

## Related

- `tools/tiny-event-emitter-guide.md` — `tiny-event-emitter`, a separate repo
  that *does* expose an `EventEmitter` class. Do not confuse the two.
- `tools/tiny-event-bus-guide.md` — `tiny-event-bus`, also distinct
- `tools/tiny-callback-guide.md` — callbacks and deferreds
