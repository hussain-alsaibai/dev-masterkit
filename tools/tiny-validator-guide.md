# tiny-validator — Stdlib Data Validation

## Repo

https://github.com/hussain-alsaibai/tiny-validator

## One-liner

Zero-dependency validation library for typed dictionaries, tool contracts, and a
practical subset of JSON Schema.

## When to Use

- You need Pydantic-like input checks without dependencies.
- You are validating tool-call arguments before side effects.
- You need a bridge from JSON Schema into a tiny-* validator.
- You want explicit, testable contracts for agent boundaries.

## JSON Schema Bridge

`from_json_schema()` converts a practical MCP/tool-call JSON Schema subset into
runtime validators.

Verified subset:

- object properties,
- required fields,
- primitive types,
- arrays,
- nested objects,
- enums,
- minimum/maximum style numeric checks where supported.

## Tool Contract Pattern

```python
from tiny_validator import from_json_schema

schema = {
    "type": "object",
    "required": ["query", "limit"],
    "properties": {
        "query": {"type": "string"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
    },
}

validate = from_json_schema(schema)
args = validate({"query": "cache invalidation", "limit": 5})
```

## Schema-Drift Repair Loop

When a prompt emits an outdated tool shape, keep validation strict. Turn the
structured path errors into a bounded repair task, validate the repaired JSON
again, and only then allow a side effect. Include the schema name, failed
payload, exact errors, and allowed values in the repair input; redact secrets
before sending it to a model. Use a maximum of one or two repairs, then reject
or escalate for human review instead of looping forever. Log `schema`, `path`,
`decision`, and `repair_attempt` with `tiny-log`.

See [Schema Drift Repair Loops With tiny-validator](https://github.com/hussain-alsaibai/tiny-validator/blob/main/reports/2026-07-14-schema-drift-repair-loops.md)
for the verified field note.

## Typed Tool Boundaries

Use tiny-validator as the last local boundary before generated arguments reach
filesystem, GitHub, browser, messaging, deployment, or billing tools. Validate
required fields, enum modes, idempotency keys, and payload shapes before any
side effect, then log accepted or rejected arguments separately from execution.

```python
from tiny_validator import Field, Schema

tool_call = Schema({
    "mode": Field(str, required=True, enum=["dry_run", "write", "notify"]),
    "target": Field(str, required=True, min_length=1),
    "idempotency_key": Field(str, required=True, min_length=12),
    "payload": Field(dict, required=True),
}, strict=True)

validated = tool_call(arguments)
```

Prefer fail-closed schemas for side-effecting tools. Unknown fields should be
rejected, not quietly ignored, unless the handler has a specific compatibility
reason to accept them.

## Operational Checklist

- Validate before issuing network, filesystem, queue, or billing side effects.
- Keep unsupported JSON Schema keywords explicit rather than silently trusted.
- Add tests for missing required fields, wrong types, and nested invalid data.
- Treat schemas as boundary contracts, not documentation-only hints.

## Tests

34/34 passing after adding the JSON Schema bridge.

## Last verified: 2026-07-15

- Repo: `hussain-alsaibai/tiny-validator`
- Commit: `84b0f8d` (schema-drift field note; JSON Schema bridge remains at
  `296079e`)
- Verification: local field note
  `reports/2026-07-15-typed-tool-boundaries.md` was reviewed during the July
  15 developer-tools report run; no new code was required for the typed
  boundary procedure.
