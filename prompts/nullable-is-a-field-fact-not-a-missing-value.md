# Nullable Is a Field Fact, Not a Missing Value

**Last verified: 2026-11-24** — `tiny-validator` 0.7.4 (`348695c`). Verified in
a REPL probe against the tagged source: `Schema({"tags": List(String(),
nullable=True)})` accepts `{"tags": None}`, `{}` still reports
`missing required field`, and `from_json_schema({"type": ["string", "null"]})`
plus `{"type": "string", "nullable": true}` both import as nullable while
`{"type": "string"}` still rejects `None`. 14 tests added, 11 red on 0.7.3,
suite 234 passed / 4 skipped.

## The problem

A validation library could express **absent** (`required=False`) but not
**present and null**. `Field.allow_none` was a read-only class property that
only `Any` overrode, so:

```python
fields.String(allow_none=True)   # TypeError: unexpected keyword argument
```

The only spelling a user could reach was:

```python
Schema({"tags": fields.List(fields.String(), required=False, default=None)})
validate({})
# -> [{'path': 'tags', 'message': 'value is null'}]
```

That schema **rejects every document** — including the empty one — because the
`None` default is validated as a *value* before the field is allowed to be
absent. The library's object model was fine; there was no way to say the thing.

## The fix: two orthogonal facts

`required` and `nullable` are separate questions and neither implies the other:

```python
Field(*, required=True, default=..., description="", nullable=False)
```

- `nullable=True` → `None` is an acceptable **value**.
- a `None` default **implies** `nullable=True`, because a `None` default *means*
  "absent is null" — rejecting it would make the idiomatic optional-null field
  impossible to declare.
- `required=False` alone still does **not** allow `None`.

`Any` now passes `nullable=True` through the constructor instead of shadowing
the property with a class attribute, so `fields.Any(nullable=False)` finally
means "any non-null value".

## The mirror defect is the one people miss

The JSON Schema bridge stripped `"null"` out of a union and built a
**non-nullable** field — so a contract imported from OpenAPI or MCP rejected
the nulls it explicitly permitted. A schema-import path that silently narrows
the contract it imports is worse than one that refuses the keyword.

```python
from_json_schema({"type": ["string", "null"]})            # accepted, and NULLABLE
from_json_schema({"type": "string", "nullable": True})    # accepted, and NULLABLE
to_json_schema(schema_with_nullable)                      # emits "nullable": true
```

Import and export must round-trip the **same** nullability. A schema is a
contract; an exporter that advertises a narrower contract than the validator
enforces hands downstream consumers a document that fails later, somewhere
unhelpful.

## What to check when auditing a validator

1. Can I say each of the four combinations — required/optional ×
   nullable/non-null? If one is unreachable, that is the bug.
2. Does a `None` default silently relax a required field?
3. Does import accept every spelling the export emits, and do both preserve
   nullability?
4. Does the plain (non-nullable) case still reject `None`? Narrowing is the
   guard against over-correction.

## Related

- `prompts/a-unit-chosen-before-rounding-contradicts-its-number.md` — same day,
  same class: two things computed separately that no longer agree.
- `tools/probing-a-boundary-in-five-lines.md`
