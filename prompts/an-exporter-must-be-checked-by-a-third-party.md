# An exporter must be checked by a third party, not by its own roundtrip

**Added:** 2026-11-12
**Last verified:** 2026-11-12 (`tiny-validator` 0.7.1 `73d4d08`; cross-check run against `jsonschema` 4.26, CI green 5/5 matrix rows)
**Class:** verification / library API
**Cost of not knowing:** every OpenAPI 3.1 body and MCP tool definition generated from the export rejected valid input — failing in the *consumer*, never in the library

## The defect

`tiny-validator`'s `validate()` reports "missing required field" only when

```python
if field.required and field.default is ...:
```

`to_json_schema()` built its `required` list from `field.required` alone:

```python
if field.required:
    required.append(key)
```

So a field written `String(default="anon")` is **optional at runtime** and was
**emitted as required**. Nothing in the library noticed, because nothing in the
library consumed the export. The failure surfaces one layer out:

```
library_ok = schema.validate({})        -> True   (accepts)
jsonschema.validate({}, to_json_schema(schema))   -> ValidationError
```

Every generated OpenAPI 3.1 document and every MCP tool definition built from
that export refused a body the library itself accepted.

## Why a roundtrip test hides it

The natural test is `to_json_schema` → `from_json_schema` → `validate`. It
passes. Both directions were written by the same person from the same wrong
assumption, so `from_json_schema` also marks the field required, and the two
errors cancel. **A roundtrip between two artefacts you wrote tests consistency,
not correctness.**

## The check that catches it

Short, permanent, and third-party:

```python
library_ok = not schema.validate(payload)

try:
    jsonschema.validate(payload, to_json_schema(schema))
    js_ok = True
except jsonschema.ValidationError:
    js_ok = False

assert library_ok == js_ok
```

`jsonschema` is a **test-only** dependency; `pytest.importorskip("jsonschema")`
keeps the zero-dependency test run intact. Parametrise it over a payload per
field shape: required-and-present, required-and-absent, defaulted-and-absent,
defaulted-and-present.

## The rule

**Any function that exports your format into another format must be validated
by a consumer that did not write the exporter.** The same applies to:

- a schema generator checked with a real JSON Schema validator, not with your own parser
- an OpenAPI emitter checked with `openapi-spec-validator`, not with your own loader
- an MCP tool definition checked by a client that rejects unknown shapes
- a serializer checked by the language runtime of the other side

**Second rule:** the fix is one line, and the one line is an *intersection* of
two truth sources. Write it so the two sources are visible together —
`field.required and field.default is ...` — because the next reader will
otherwise "simplify" it back to `field.required`.

**Third rule:** when a version guard exists, use it. Both version guards
(`test_version_consistency`) caught README badge and `package.json` drift on the
0.7.1 bump. That is the one class of defect that can be caught by reading
rather than executing, so it should never be the class that ships.
