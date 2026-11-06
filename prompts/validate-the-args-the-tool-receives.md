# Validate The Args The Tool Receives, Not The Ones You Sent

**A contract check on the *prepared* payload proves nothing about the
*received* payload.**

> Found 2026-11-06. Recorded from `tiny-validator`'s field note
> `reports/2026-11-06-tool-call-contract-regression.md`, written the same day.
> **Last verified:** 2026-11-06 (18:00 UTC) — the snippet below was executed
> against `tiny-validator` `from_json_schema()` and `ValidationError` before
> publication of the field note; the `gate()` snippet is illustrative and is
> NOT claimed as executed.

## The Rule

> **A tool call is a contract. Validate at the boundary the tool actually sits
> behind — after serialisation, on the payload the receiver will parse.**

Agent tool calls regress: a field is renamed, an enum gains a value, `required`
moves. The agent's prompt still emits the old shape and the failure surfaces as
a *tool error at side-effect time* instead of a *mismatch at validation time*.
Opening half a PR cannot be un-validated.

## The gap that makes the check useless

```python
# Requires tiny-validator (pip install tiny-validator); imports verified 2026-11-06.
# This snippet is illustrative, not executed — the note's own example is.
from tiny_validator import from_json_schema, ValidationError

OPEN_PR = from_json_schema({
    "type": "object",
    "required": ["repo", "title", "branch"],
    "properties": {
        "repo": {"type": "string", "pattern": r"^[^/]+/[^/]+$"},
        "title": {"type": "string", "minLength": 8, "maxLength": 120},
        "branch": {"type": "string", "minLength": 1, "maxLength": 120},
        "draft": {"type": "boolean", "default": True},
    },
    "additionalProperties": False,
})

def gate(payload: dict) -> dict:
    """Validate AT THE BOUNDARY, after serialisation."""
    try:
        return {"ok": True, "args": OPEN_PR(payload)}
    except ValidationError as exc:
        return {"ok": False, "errors": exc.errors}
```

`payload` passes a local check, a serialiser drops `None` values, the tool
receives a dict missing a required field. Validate both sides and assert they
agree — the same idea with better evidence.

## Four checks worth having in CI

1. **Schema snapshot** — record the published schema, diff it per release. A
   renamed argument breaks callers silently.
2. **Round-trip parity** — `validate(serialise(validate(p)))` must equal the
   first result. If the second pass rejects what the first accepted, the
   serialiser is changing the contract.
3. **Negative case per required field** — remove each and assert rejection. A
   schema that accepts its own missing field is worse than none, because it
   reports success.
4. **Enum drift** — adding a value is backwards-compatible for callers and
   forward-breaking for servers. Pick a direction on purpose.

`additionalProperties: false` is the load-bearing default: a typo'd key is
silently dropped by a permissive schema, and the tool runs with a default the
caller never chose.

## What this does not fix

Validation proves shape, never intent. A perfectly-shaped
`{"repo": "attacker/repo", ...}` passes every schema here. Authorization
belongs after validation and is not the validator's job.
