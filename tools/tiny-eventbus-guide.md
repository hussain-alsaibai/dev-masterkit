# tiny-eventbus — Durable Pub/Sub with Replay

## Repo
https://github.com/hussain-alsaibai/tiny-eventbus

## One-liner
Zero-dependency durable pub/sub for agent workflows: append-only JSONL event history, topic filters, wildcard subscribers, cursor replay, and awaitable one-shot events.

## Install
```bash
npm install tiny-eventbus
```

## Quick Example

```js
import { EventBus } from "tiny-eventbus";

const bus = new EventBus({ path: "./events.jsonl" });

bus.subscribe("request.completed", (event) => {
  console.log(event.payload.requestId, event.payload.status);
});

await bus.publish("request.received", { requestId: "req_42" });
await bus.publish("request.completed", { requestId: "req_42", status: 200 });
```

## Replay and cursors

```js
const lastSeenOffset = 128;

bus.subscribe("agent.", handler, {
  replay: true,
  fromOffset: lastSeenOffset,
  prefix: true
});
```

## One-shot waits

```js
const approved = await bus.once(
  "approval.received",
  (event) => event.payload.taskId === "deploy-42",
  { timeoutMs: 60_000 }
);
```

## Properties

| Property | How |
|----------|-----|
| Durability | Append-only JSONL log |
| Replay | Subscribe from beginning or from a stored offset |
| Topic filters | Exact topic and prefix matching |
| Wildcards | `subscribeAll()` for audit/log sinks |
| Awaitable events | `once(topic, predicate, timeout)` |
| Rotation | Automatic log rotation at `maxLogBytes` |
| Fault isolation | Subscriber errors emit `subscriber_error` |

## CLI

```bash
tiny-eventbus history --topic=request.completed ./events.jsonl
tiny-eventbus tail ./events.jsonl
```

## Testing

- **17/17 tests passing**
- Verified with Node's built-in test runner
- 0 runtime dependencies

## Agent workflow fit

Use `tiny-eventbus` when a cron or agent process needs more durability than `EventEmitter`, but Redis/Kafka would be unnecessary:

- audit every inbound webhook and model call
- replay missed events after restart
- wait for an approval or external callback
- fan out structured events to logs, metrics, or notification workers

Last verified: 2026-07-06
