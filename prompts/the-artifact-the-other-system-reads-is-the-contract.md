# The artifact the *other* system reads is the contract

**Last verified: 2026-11-26** — used to find and fix two shipped defects in one
day (`tiny-validator` 0.7.5 `161f444`, `snapdb` 0.18.5 `8a87963`). Every claim
below was re-executed in this container at 17:00Z against freshly cloned trees:
`246 passed / 4 skipped` and `277 passed / 22 skipped`.

**Class:** verification / library API
**Cost of not knowing:** an export that outlives the constraint it came from,
and a record that outlives the caller's payload — both shipped silently, both
with a fully green suite.

## When to use it

For every **write API** and every **contract-emitting API** (an exporter, a
schema generator, a serializer, an MCP tool definition, a renderer), ask:

> **Which artifact does a second system read, and does a test assert on *that*
> artifact?**

If the answer is "the in-memory object", the test is not about the contract.

A validation test asks *"does the system reject a bad value?"*. Nothing in that
question covers:

- *"does the system still **say** what it enforces?"* — the export
- *"does it **keep** what the caller did not mention?"* — the record

## The two failures this finds

### 1. The export outlived the constraint (import-only state)

`tiny-validator` 0.7.5. `from_json_schema` had always enforced `enum`:

```python
doc = {"type": "object",
       "properties": {"role": {"type": "string", "enum": ["admin", "user"]}}}
tv.from_json_schema(doc).validate({"role": "superadmin"})
# -> [{'path': 'role', 'message': "value must be one of ['admin', 'user']"}]
```

The import added a **validator** and never a **constraint**, and
`to_json_schema` builds from `field.constraints`, not from validator messages.
So the export simply did not mention `enum`:

```
before  to_json_schema -> {'role': {'type': 'string'}}
after   to_json_schema -> {'role': {'type': 'string', 'enum': ['admin','user']}}
```

The library rejected `"superadmin"` while publishing a contract that **accepted
every string**. Only the consumers — OpenAPI documents, MCP tool schemas,
generated clients — saw the wrong one. No validation test can see this.

Measured after the fix: the export carries `enum`, and the document also now
round-trips `additionalProperties: False` (emitted, and honoured on re-import).

**The probe:** `to_json_schema(from_json_schema(doc))` and compare against `doc`
**field by field**, plus one reject call on the imported schema.

### 2. The record outlived the caller's payload (write API)

`snapdb` 0.18.5. `DocumentStore.update(idx, doc)` wrote `doc` as the entire row.
Fixed-width rows plus a decoder that omits null placeholders meant every
unnamed field decoded as *absent*:

```
insert({"name":"alice","age":30,"role":"admin"})
update(0, {"age":31})
get(0)   ->  {'age': 31}        (name and role gone)

after 0.18.5:
update(0, {"age":31})  -> {'name':'alice','age':31,'role':'admin'}
update(99, {...})      -> IndexError: no document at index 99
replace(0, {...})      -> the old whole-record behaviour, named honestly
```

Nothing raised. The row existed. The field the caller edited was correct. That
is the worst shape for a store used as an agent audit trail.

## The two rules

**Rule 1: name the second consumer and assert *its* artifact.** The export, not
the schema object. The stored record, not the argument you passed.

**Rule 2: a write API's name is a contract, and the dangerous payload is the
partial one.** `update` means *change what I named*; `replace`/`put` mean *make
this the record*. When a function is spelled like the first and behaves like
the second, the caller's correct mental model becomes the bug.

All **264** existing `snapdb` tests passed a **complete** record to `update` —
the single spelling where a rewrite and a patch are indistinguishable. Add one
test per write API with the **minimum valid payload**; that is the payload that
separates them.

**Rule 3: a write that has nowhere to go must raise.** `update` on a
nonexistent row used to write a placeholder row: no error, a new row, and a
caller who believes an existing record was modified. Silence is the defect, not
the exception.

## Checklist

```
[ ] exporter:                              to_json_schema(from_json_schema(doc)) == doc (modulo defaults)
[ ] exporter, negative:                    imported schema rejects a value the export forbids
[ ] write API, minimum payload:            update(id, {only_the_changed_field}) keeps the rest
[ ] write API, replace:                    replace(id, doc) makes doc the record
[ ] write API, missing target:             raises, does not create
[ ] explicit None:                         clears (patch) — distinct from omitted (keep)
```

## Why the green suite is not evidence

This is the third instance of one family recorded in this repo:

| date | shape | why green tests missed it |
|---|---|---|
| 2026-11-24 | value vs unit (`bytes_human`) | tests asserted the value, not that the number and its label agree |
| 2026-11-25 | declared vs enforced (`cors`) | the browser enforced the rule, so no library test could |
| 2026-11-26 | export vs validator / payload vs record | tests asserted the in-memory object, never the second consumer's artifact |

Same defect one level out each time: **the test and the bug share an
assumption.**

Related prompts: `an-exporter-must-be-checked-by-a-third-party.md`,
`a-roundtrip-tests-consistency-not-correctness.md`,
`name-who-enforces-it-and-which-path.md`.
