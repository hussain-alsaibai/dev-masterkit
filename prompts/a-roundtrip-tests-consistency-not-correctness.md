# Export is half a contract: a round trip tests consistency, not correctness

**Last verified:** 2026-11-13 (12:00 EST) — `tiny-validator` 0.7.1 and
`tiny-config` 0.4.1 audited; four drift classes found, all in the **permissive**
direction (the direction that ships silently).

## The rule

> **A round-trip test is export -> import -> REJECT.** Asserting on the exported
> dict passes while the importer throws the constraint away.

| library | exported | validator did |
|---|---|---|
| validator 0.7.1 | `Slug`/`Regex`/`HexColor` -> bare string | rejected `"Not A Slug"` |
| validator 0.7.1 | `IP(version=4)` -> no `format` | rejected `999.1.1.1` |
| validator 0.7.1 | `format: ipv4` imported as `String` | accepted `::1` |
| config 0.4.1 | masked `secret_ref`, `tokenizer` | hid the Vault path |
| config 0.4.1 | kept `db_password` | logged the credential |

The `IP` row was correct in the export and lossy in the import — an
export-only test would have been green on a broken round trip. Prove both
halves:

```python
assert rejects(original, bad)      # the corpus entry is genuinely invalid
assert rejects(roundtrip, bad)     # the conversion kept the constraint
```

Same shape as the `tiny-validator` roundtrip that passed on 2026-11-12 because
both halves shared the wrong assumption and cancelled. A round trip between two
copies of your own belief is a tautology.

## Grep every registration site after adding a mechanism

`set_constraint` was added for `String` and `Integer` in v0.6.0. `Slug`,
`Regex` and `HexColor` kept their pattern in a closure written *before* the
mechanism existed, and were never swept. New mechanism => grep every
`add_validator(` call.

## A format you cannot enforce must not be exported

`tiny-validator` emits no `format` for unversioned `IP()` — no standard tag spans
v4+v6, and a tag nothing validates reads as a guarantee.

## A substring is the wrong operator for secret names

`tiny-config` used `key.lower() in SECRET_WORDS`, which masked `secret_ref`
(contains `secret`) **and** kept `db_password` (is not `password`). Equality OR
**suffix** is the operator: suffix because `db_password` *names* the secret and
`password_file` names a path. Pointer values (`vault://`, `awssm://`, `op://`,
`env://`) and empty strings pass through even under an explicit `redact=` entry —
masking a pointer destroys the incident record, not the secret.
