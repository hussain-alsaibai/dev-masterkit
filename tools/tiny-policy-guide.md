# tiny-policy - ABAC Policy Engine for Agents

## Repo
https://github.com/hussain-alsaibai/tiny-policy

## One-liner
Zero-dependency attribute-based authorization for AI agents and HTTP APIs: JSON policies, glob matching, deny-overrides, metrics, and explainable decisions.

## Install
```bash
npm install tiny-policy
```

## Quick Example

```js
import { PolicyEngine } from "tiny-policy";

const engine = new PolicyEngine({
  policies: [
    {
      id: "tenant-read",
      effect: "allow",
      actions: ["customer.read"],
      resources: ["customer.*"],
      conditions: {
        "subject.role": { in: ["support", "admin"] },
        "resource.region": { eq: "eu" }
      }
    },
    {
      id: "blocked-user",
      effect: "deny",
      actions: ["*"],
      resources: ["**"],
      conditions: {
        "subject.status": { eq: "blocked" }
      }
    }
  ]
});

const decision = engine.evaluate({
  subject: { role: "support", status: "active" },
  action: "customer.read",
  resource: { type: "customer", region: "eu" },
  resourceId: "customer.123"
});

if (!decision.allowed) {
  throw new Error(`Denied by ${decision.policyId ?? "default"}`);
}
```

## Policy shape

```json
{
  "id": "support-read",
  "effect": "allow",
  "actions": ["ticket.read"],
  "resources": ["ticket.*"],
  "conditions": {
    "subject.department": { "eq": "support" },
    "resource.priority": { "in": ["low", "medium", "high"] }
  }
}
```

## Condition operators

| Operator | Use |
|----------|-----|
| `eq` / `ne` | Exact equality / inequality |
| `in` / `nin` | Membership checks |
| `gt` / `gte` / `lt` / `lte` | Numeric or ordered comparisons |
| `contains` | Array or string containment |
| `startsWith` / `endsWith` | String prefix/suffix checks |
| `matches` | Glob match on a string value |
| `exists` | Presence or absence checks |

## Glob semantics

| Pattern | Meaning |
|---------|---------|
| `*` | One segment; does not cross `.` |
| `**` | Any number of segments |
| `?` | One character |

Use `user.*` for `user.read`; use `user.**` for `user.read.list`.

## Agent workflow fit

Put `tiny-policy` in front of any tool call that can mutate state, spend money, read private data, or call an external system:

1. Normalize the request into `subject`, `action`, and `resource`.
2. Load policies from versioned JSON with `PolicyLoader.load(dir)`.
3. Evaluate before calling the tool.
4. Emit `decision.reason`, `policyId`, and metrics to logs/traces.
5. Prefer deny-by-default for production agents.

## Testing

- **19/19 tests passing**
- Benchmark: about **1.5 us/eval**
- 0 runtime dependencies

## Verified limitations

- Condition values are static. Cross-attribute comparisons such as `subject.tenant == resource.tenant` should be handled by a small pre-normalization layer or a future template feature.
- Glob semantics are intentionally segment-oriented; `*` does not match dots.

Last verified: 2026-07-07
