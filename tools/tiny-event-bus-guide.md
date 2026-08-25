# tiny-event-bus Guide

**Repository:** https://github.com/hussain-alsaibai/tiny-event-bus
**License:** MIT
**Last verified:** 2026-08-25

## What It Is

Zero-dependency in-process pub/sub event bus for Python. Single file (~400 LOC), pure stdlib.

## What It Does

- Topic-based subscriptions with wildcard support (`user.*`, `agent.#`)
- Sync and async publish (`publish_async` awaits async handlers)
- Dead-letter queue (DLQ) for failed handler logging
- Middleware hooks (`on_publish`, `on_subscribe`, `on_unsubscribe`)
- Priority ordering — higher priority handlers run first
- Once-only subscriptions (`once=True` auto-unsubscribes after first fire)
- Event filtering — handlers returning `False` stop propagation
- Full type hints, Python 3.9+

## When to Use It

- AI agent tool event logging (tool.call / tool.result / agent.error)
- Plugin systems with inter-component pub/sub
- Multi-agent messaging within a single process
- Replacing `blinker`, `pypubsub`, or custom observer patterns

## Quick Example

```python
from tiny_event_bus import EventBus

bus = EventBus()

@bus.subscribe("tool.call")
def log_call(event):
    print(f"Calling: {event['tool']}")

bus.publish("tool.call", {"tool": "web_search", "args": {}})
```

## Related

- [tiny-workflow-engine](tools/tiny-workflow-engine-guide.md) — DAG orchestrator (consumes events)
- [tiny-event-emitter](tools/tiny-event-emitter-guide.md) — simpler emitter pattern
