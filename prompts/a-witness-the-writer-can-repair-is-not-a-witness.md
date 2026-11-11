# A witness the writer can repair is not a witness

**Discovered:** 2026-11-11 (tiny-audit 0.2.0, `242b86b`)
**Last verified:** 2026-11-11 — `verify()` run against a log truncated from 3
entries to 1, before and after the fix

## The bug

`tiny-audit`'s `verify()` checked `prev_hash` and the HMAC of every line. A
**truncated** log passed: the surviving lines chain and sign perfectly, so
every check it performed was satisfied by a log whose tail had been deleted.
Tail truncation is the cheapest tamper there is and the one an audit log exists
to catch.

Measured on 0.1.0: 3 entries → `verify()` True; rewrite to 1 entry →
`verify()` True.

## The fix, and the first version that undid itself

`AuditEntry.seq` is now inside the HMAC message, so middle deletion and
reordering surface as `Sequence gap`. Truncation needs something outside the
log: an optional `high_water_path=` sidecar holding the highest `seq` ever
written, which `verify()` compares against.

The first version of that fix was self-defeating. The constructor wrote the
observed length into the sidecar **unconditionally**, so reopening a truncated
log wrote the truncated length over the record of its real length, and
`verify()` then compared the log to itself. It passed. It would always pass.

The write must be **raise-only**:

```python
observed = last_seq(log)
if observed > high_water:
    high_water = observed      # raise the water mark
    write(high_water_path, high_water)
# never lower it, and never rewrite it from a log that verify() has not trusted
```

## The rule

> If the same code path that can damage the evidence also updates the record
> of what the evidence should be, the record is not a witness.

This generalises past audit logs: checksums written by the writer of the data,
"last known good" markers refreshed on every start, migration markers advanced
by the migration being re-run. The witness must be written by a path that the
damage cannot reach, or it is a copy of the thing it is supposed to check.

## Be explicit about the limit

Without the sidecar, truncation is **still undetectable** — a valid 1-entry log
is indistinguishable from a valid 1-entry log. 0.2.0 documents that limit and
pins it with a test, because a documented limit is a design decision and an
undocumented one is a bug.

## Prove it against the old version

9 new tests, all 9 failing against 0.1.0. A security fix whose tests pass on
the vulnerable version is a test of the test harness.
