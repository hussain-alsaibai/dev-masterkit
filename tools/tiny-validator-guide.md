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

## Schema Export Must Record, Not Reconstruct

`to_json_schema()` and `to_openapi_schema()` are contract surfaces: whatever
they omit becomes an unconstrained field in every downstream consumer's
generated docs and tool definition.

Until v0.6.0 they recovered field constraints by parsing the validator's own
error message strings. That failed in both directions:

- **Silent loss.** `String(choices=[...])` and `pattern` never appeared in the
  exported schema, so an OpenAPI consumer saw a bare `string` and an MCP
  client sent anything.
- **Silent invention.** Arbitrary validator prose containing `must be at least
  999 characters of prose` produced a `minLength: 999` that no caller ever
  declared. A constraint read out of prose is not a constraint.

The fix is `Field.set_constraint()`, which records the constraint when the
field is constructed. The exporter reads the record. Backward compatible, and
it removes the entire class: no string parsing anywhere in the export path.

**When you add a constraint keyword, add it to the recorded set, not to a
parser.** Any constraint that exists only as text inside an error message is
one refactor away from being invented for a field that never had it.

## Tests

114 passing as of v0.6.0 (95 before this cycle, plus 19 new).

## Last verified: 2026-10-22

- Repo: `hussain-alsaibai/tiny-validator`
- Version: v0.6.0, commit `f0b4bb2`
- Verification: 114/114 by test run on 2026-10-22, plus a hand audit of the
  exporter confirming constraints are read from `Field` records rather than
  from validator error strings.
