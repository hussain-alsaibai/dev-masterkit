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

## Operational Checklist

- Validate before issuing network, filesystem, queue, or billing side effects.
- Keep unsupported JSON Schema keywords explicit rather than silently trusted.
- Add tests for missing required fields, wrong types, and nested invalid data.
- Treat schemas as boundary contracts, not documentation-only hints.

## Tests

34/34 passing after adding the JSON Schema bridge.

## Last verified: 2026-07-13

- Repo: `hussain-alsaibai/tiny-validator`
- Commit: `296079e`
- Verification: full local test suite passing.
