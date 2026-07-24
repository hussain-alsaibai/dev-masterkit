# tiny-callback Guide

**Repo:** [hussain-alsaibai/tiny-callback](https://github.com/hussain-alsaibai/tiny-callback)  
**Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> Zero-dependency async callbacks, promise pattern, and event emitter for Python.

## What it does

Provides async callback registration, promise-style futures, and event emitter patterns — all in pure Python stdlib with zero external dependencies.

## When to use

- **Async callback chaining** — register callbacks on async operations without third-party async libs
- **Promise/Deferred pattern** — represent pending async results as first-class objects
- **Event-driven architectures** — decouple components with event emission and subscription
- **Middleware systems** — register and compose async middleware layers

## Key patterns

```python
from tiny_callback import EventEmitter, Promise

emitter = EventEmitter()

@emitter.on("data")
def handle_data(data):
    print(f"Got: {data}")

emitter.emit("data", {"key": "value"})

# Promise pattern
promise = Promise()
promise.then(lambda x: x * 2).catch(lambda e: print(f"Error: {e}"))
promise.resolve(21)
```

## Related

- `tiny-eventbus` — durable pub/sub with replay (topic-based, persistent)
- `tiny-chain` — LLM processor with callback hooks for streaming responses
- `tiny-workflow` — DAG orchestrator using callbacks for step completion
