# Answering A Review When The Fix Is The Next Bug

**Use when:** a reviewer's reproduction passes, and the fix you are about to
push is a *rewrite of a predicate or a signature* rather than a one-line
correction — especially on the second or third round of the same finding.

**Do not use when:** the reviewer named a line and the line was wrong. That is a
patch; this is a procedure for the case where the shape changed.

**Last verified:** 2026-11-16 — written against `gortex` PR #1418 (four review
rounds, two of which found defects introduced by the previous fix) and
`blixvip/NullMotion` #75 (a prefix-strip placement bug found by reading the
handler top to bottom).

---

## 1. Classify the finding before touching code

| finding shape | what to do | what not to do |
|---|---|---|
| wrong constant / off-by-one | patch the line, add the failing test | rewrite the function |
| wrong operator (`&&` vs `\|\|`) | re-derive the truth table first | swap the operator and stop |
| wrong **kind** of test (count vs membership) | rewrite, then enumerate new wrong cases | assume the reviewer's example is the space |
| wrong data-flow (a helper returns too little) | change the signature so the compiler finds every caller | thread a new parameter through and hope |
| wrong order of operations | move the step, then re-check every branch above it | patch the branch that was reported |

The third and fourth rows are where a fix creates the next bug. Both are visible
*only* if you treat the new shape as new code.

## 2. The differential table

Keep the old function. If it is on disk, the old body is one `git show` away:

```
git show origin/main:internal/x/guard.go > /tmp/old_guard.go
```

Run both over one fixture set and publish both columns:

```
case                         old   new   expected
empty                        skip  fail  fail
single manual_config         pass  pass  pass
duplicate manual_config      fail  pass  pass
manual + cli_track           pass  fail  fail   <- first fix, still right
```

Two rules about the table:

- **The `expected` column is derived from the data shape**, not from either
  implementation.
- **Every cell where old and new disagree is either the bug you were sent or a
  bug you just introduced.** Name it; do not let the reviewer find it.

## 3. Signatures over assertions when the data flow is the fault

`configuredRepoPaths() []string` could not express "unknown". The fix was
`([]string, error)`, and the value of that choice was mechanical: every stub,
seam and caller failed to compile, so none of them could silently keep the old
assumption. A new boolean parameter would have compiled everywhere and been
ignored in half of them.

When you change a signature that a test seam holds, update the stubs in the
same commit and say so in the reply — a reviewer checking the seam will wonder
whether the change is load-bearing.

## 4. Both output formats, both directions

A collector that reports to JSON and to a human has two contracts:

- JSON: `checked: false`, a machine-readable reason, **no** findings array.
- Human: names the thing that failed, and **never** emits the clean phrase.

Assert the *absence* of the clean phrase. `grep -c "no legacy state found"` must
be 0 in the failure fixture. A test on `checked: false` alone passes on a
document that then closes with "no problems found".

## 5. State the verification limit in the reply

If the package does not compile on the reviewer's machine either, say which
signals you do have, in this order of strength:

1. package tests that ran (count them)
2. harness tests with the functions copied verbatim (count, and give the pre-fix
   failure count)
3. compiler type-check reachable only after stubbing an unrelated dependency
4. `gofmt -l` on exactly the changed files, filtered `go vet`
5. nothing — then say nothing

"All tests pass" with a package that cannot compile is the one thing that
converts a good fix into a lost review. The honest form is:

> `go test ./cmd/gortex/` cannot run here (198 cgo build-constraint files are
> excluded on this host). The functions were copied verbatim into a harness:
> **17/17 pass post-fix, 4 failures pre-fix**. `gofmt -l` and a filtered `go
> vet` are clean on the changed files.

## 6. When a `vet` is clean, ask what it type-checked

A clean `go vet` on a tree whose test imports were never compiled is not a
clean bill. The tell: the package fails on grammar exclusions *before* the
compiler type-checks the `_test.go` files, so a missing import ships.

The ten-minute fix: stub the failing grammars, recompile, let the type checker
reach the tests, then restore the stubs from backups and confirm `git status` is
clean apart from the intended files. In #1418 this caught a missing `errors`
import immediately.

## 7. Reply structure that has worked

```markdown
## Fixed in <sha>

<one paragraph: what the wrong premise was>

**Change:** <the shape change, named — "exclusion list -> membership test",
not "fixed the guard">

| case | before | after |
|---|---|---|

**Tests:** <count and file>; proven to fail on <base>: <n> failures.

**Verification limit:** <what cannot run here and what ran instead>
```

Naming the shape change ("count -> membership") is what stops a fourth round:
it tells the reviewer which space you already checked and invites them into the
cells rather than back to the start.

---

## Checklist

- [ ] Finding classified: patch vs rewrite
- [ ] Truth table re-derived from the data, all four boundary inputs
- [ ] Old body retained for the differential run
- [ ] Signature changed where the data flow could not express "unknown"
- [ ] Both output formats tested; clean phrase asserted absent
- [ ] Pre-fix failure count recorded, not just post-fix pass count
- [ ] Verification limit stated in the reply, in order of strength
- [ ] `gofmt -l` restricted to changed files; `go vet` filtered to them
