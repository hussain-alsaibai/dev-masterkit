---
name: a-list-of-records-is-not-a-list-of-values.md
description: Use when a predicate counts entries in a slice whose elements are projected from rows — `len(x) == 1`, `len(x) != 1`, uniqueness assumed — because a key that can repeat makes the count describe the row set, not the value set.
---

# A list of records is not a list of values

## The prompt

> Before writing `len(things) == 1`, ask what one element of that slice **is**.
> If it is a row from a table, the same value can appear twice, and a count is
> not a membership test. Classify the value set, never the entry count.

## What happened

`gortex` PR #1418, reviewer finding P2-6 (third round on the same guard).

The guard was meant to answer one question: *is this checkout attributed to a
tool, or is it only manually configured?* The previous fix replaced an
exclusion list (`cli_track || mcp_track`) with a positive test, which was the
right direction — but implemented it as a **count**:

```go
kinds := overview.IntentKinds()
if len(kinds) != 1 { return }      // "not exactly one kind"
if kinds[0] == "manual_config" { warn() }
```

The premise is that one intent kind means one entry. Verified against the
source before changing anything:

- `internal/indexer/checkout_overview.go:338-350` appends
  `string(intent.SourceKind)` **once per row** returned by
  `ListTrackingIntents`
- `internal/graph/store_sqlite/catalog.go:1149-1155` upserts with
  `ON CONFLICT(checkout_id, source_kind, source_locator)`

The conflict key is `(checkout_id, source_kind, source_locator)` — so one
checkout can hold **two live rows of the same kind** under different locators.
A checkout recorded under an old root and then a new one yields
`["manual_config", "manual_config"]`: no CLI, MCP or project attribution, and a
genuinely unattributed checkout.

`len(kinds) != 1` is true, so the guard returned early and **suppressed the
warning**. A checkout with nothing recording its provenance was reported clean.

**Fix:** classify the set.

```go
func isManualConfigOnly(kinds []string) bool {
    if len(kinds) == 0 { return false }
    for _, k := range kinds {
        if k != "manual_config" { return false }
    }
    return true
}
```

Duplicates allowed; every attributed kind still disqualifies the row; an empty
list is not "clean", it is "nothing recorded".

**Proof:** the new predicate was evaluated against the old one over nine intent
sets. New: correct on all nine. Old: wrong on exactly two — the duplicate-row
cases the reviewer named. Two regressions added:

- `TestLegacyStateUnattributedAllowsDuplicateManualConfigRows` (two and three
  identical rows — passes on the new predicate, fails on the old)
- `TestLegacyStateUnattributedExcludesMixedIntentRows` (four mixed sets — so
  "allow duplicates" cannot be implemented as "allow anything")

The file now holds twelve `TestLegacyState*` tests. `go vet` clean, `gofmt -l`
empty on all changed files, PR head `81fbce5c6`, 6 files +1336/-0.

## The rule

1. **`len(x) == 1` on a projection is a count of rows wearing the name of a
   value.** If the element type names a source (`SourceKind`, `SourceLocator`,
   `intent_id`), assume it can repeat and write a membership test.
2. **Ask what the slice's uniqueness invariant is, and where it is enforced.**
   Here it was enforced nowhere — the DB's conflict key included the locator,
   which is exactly the field that allows a repeat.
3. **Replacing an exclusion list with a positive test is a rewrite, not a
   patch.** The new shape has its own wrong cases; enumerate them (empty,
   singleton, duplicate, mixed) before claiming the bug is gone.
4. **A guard that suppresses a warning must be tested in the direction that
   fires it.** The old tests all exercised the "warn" path; none exercised
   "should have warned and did not".
5. **Prove the new predicate against the old one over a fixture set**, not just
   against the reviewer's reproduction. The table (9 sets, old wrong on 2) is
   the artifact that shows the fix is a superset of the old behaviour wherever
   the old behaviour was right.

## Test skeleton

```go
cases := []struct{ name string; kinds []string; want bool }{
    {"none",          nil,                              false},
    {"manual only",   []string{"manual_config"},        true},
    {"manual twice",  []string{"manual_config","manual_config"}, true},
    {"mixed",         []string{"manual_config","cli_track"}, false},
    {"cli only",      []string{"cli_track"},            false},
}
```

Run the same table against the old function and the new one, and record both
columns. A table that is green on the new function alone proves nothing about
what changed.

---

**Last verified:** 2026-11-16 — source lines re-read at the cited paths before
the change; nine-set comparison run in this session; `go vet` and `gofmt -l`
clean on the rebased tree; PR `gortex` #1418 head `81fbce5c6`, +1336/−0 across 6
files, reply posted. Note the verification limit: `go test ./cmd/gortex/`
excludes 198 cgo build-constraint files on this host, so the harness — not a
package test — is what ran.
