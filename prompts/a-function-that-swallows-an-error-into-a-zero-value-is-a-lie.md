---
name: a-function-that-swallows-an-error-into-a-zero-value-is-a-lie.md
description: Use when a helper returns nil/empty for both "nothing to report" and "could not find out" — a failure becomes an absence, and an absence becomes a clean report. Also use when a callee already draws the line and the caller collapsed it.
---

# A function that swallows an error into a zero value is a lie amplifier

## The prompt

> Which two things does this `return nil, nil` mean? If the answer is "nothing
> here" and "I could not look", every caller downstream will treat the second
> as the first — and a check that could not run will report as a check that
> passed.

## What happened

`gortex` #1418, fourth review finding. The legacy-state collector needed the
list of repositories from the user's global config:

```go
func configuredRepoPaths() []string {
    paths := []string{}
    for _, r := range cfg.Repositories { paths = append(paths, r.Path) }
    return paths      // nil on read error, nil on parse error, nil on nothing
}
```

Two distinct situations collapsed into one return value:

| situation | correct meaning | what the caller got |
|---|---|---|
| config has no repositories | nothing to check | nothing to check |
| config could not be READ | **unknown** | nothing to check |
| config could not be PARSED | **unknown** | nothing to check |

The collector then reported a **completed check** with no legacy state found —
an inventory it never loaded.

`config.LoadGlobal` had already drawn the line: a missing file returns
`(gc, nil)`, a parse failure returns `(nil, err)`. My reader called it and threw
the error away in one line.

**Fix:** make the failure visible in the return type and fail closed in the
collector.

```go
func configuredRepoPaths() ([]string, error)

paths, err := configuredRepoPaths()
if err != nil {
    c.Checked = false
    c.Skipped = "global config unreadable: " + err.Error()
    return
}
```

`doctorConfiguredPaths` changed shape as a seam, and its stubs were updated
with it — a seam whose signature changes is a compile-time guarantee that no
caller silently keeps the old assumption.

**Regression:** `TestLegacyStateConfigFailureIsNotAnEmptyConfig` covers **both
output formats** — JSON (`checked: false`, `skipped` carrying the reason, no
findings array) and human (names the global config, and never emits
`no legacy state found`). The human-format assertion on the *absence of the
clean phrase* is the one that matters: a test asserting only `checked: false`
would pass on a report that still told the user it was clean.

## The rule

1. **A zero value is an assertion of absence.** Returning `nil` from a function
   that can fail asserts "there were none", which you do not know.
2. **Read the callee before reinventing its distinction.** `LoadGlobal` already
   separated missing from unparseable. Re-deriving that logic from scratch is
   how the distinction got lost — one `if err != nil { return nil }` later.
3. **Fail closed, and name the cause.** A skipped check must say *what* it could
   not do (`global config unreadable`), not merely that it skipped. The reason
   string is the only artifact a user has.
4. **Assert on the absence of the clean phrase, not on the presence of a flag.**
   Both formats, both directions.
5. **A seam's signature is a review surface.** Changing `func() []string` to
   `func() ([]string, error)` forced every stub and holder to be revisited —
   that is the point, not the cost.

## The verification gap underneath this one

`go vet` reported **clean** on the rebased tree. It had never type-checked the
test files: the package fails on cgo grammar exclusions before the compiler
reaches them, so a missing `errors` import would have shipped broken.

Stubbing the four failing grammars (`cpp`, `swift`, `scala`, `kotlin`) let the
package compile far enough for the compiler to check the test files — and it
caught the missing import immediately. Stubs were then restored from backups and
the tree confirmed clean apart from the two files the change touches.

**Rule: when your verification cannot reach the code you changed, it has not
verified anything.** "vet was clean" meant only "vet got far enough to have
opinions". See `tools/review-without-a-buildable-tree.md` for the harness; this
entry adds the case where the harness compiles but the *imports* are still
unchecked until the dependency is stubbed.

## Proof

An isolated harness runs the old and new collector side by side:

| | JSON | human |
|---|---|---|
| old | `checked=true`, no findings | `no legacy state found` |
| new | `checked=false`, `skipped` carries reason | names the global config, never claims clean |

Head `2df5cb4e7`, rebased onto current upstream, 6 files +1422/-0, reply posted.

---

**Last verified:** 2026-11-16 — old/new harness run in this session; both output
formats exercised; the stub-and-recompile check run and the missing `errors`
import caught by it, then fixed. `gortex` #1418 head `2df5cb4e7`.
