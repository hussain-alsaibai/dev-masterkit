# tiny-circuit — Zero-Dep Circuit Breaker (Node.js)

## Repo
https://github.com/hussain-alsaibai/tiny-circuit

## One-liner
Zero-dependency **circuit breaker for Node.js**. Plain JS, ~250 lines, 25+
tests. Fails fast when a downstream service starts failing and recovers
automatically.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented a **Python** API —
`pip install tiny-circuit` and `from tiny_circuit import circuit_breaker, Result`.
**Neither exists.** `tiny-circuit` is a **JavaScript/Node.js** package
(`circuit.js`, `index.js`, `circuit.test.js`, `package.json` upstream — no
Python files at all). It is not installable with pip.

Verified upstream layout:

```
README.md
circuit.js
circuit.test.js
index.js
package.json
```

Use it from Node, not Python:

```js
const { circuitBreaker } = require("tiny-circuit");
```

## Why It Matters

When a downstream service (AI API, database, queue) starts failing, stop
hammering it. Fail fast, recover automatically, and surface the failure as a
structured error your agent can reason about.

## Related
- `tools/tiny-circuit-breaker-guide.md` — `tiny-circuit-breaker`, the **Python**
  equivalent with `CircuitBreaker` / `CircuitOpen`
- `tools/tiny-retry-guide.md` — retries with backoff plus a circuit breaker
- `tools/tiny-sentinel-guide.md` — combined circuit breaker + rate limiter + timeout
