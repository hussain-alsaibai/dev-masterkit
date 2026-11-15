# Reviewing Code You Cannot Build: The Go Pre-Fix Harness

**Last verified:** 2026-11-15 — every command and number below was run in this
container, this session, against `hussain-alsaibai/gortex` at
`doctor-legacy-state` (`e1185a5a0`), PR #1418.

**The situation:** a maintainer review raises a correctness finding, you fix
it, you cannot run a single line of the test suite, and you have to prove the
fix before pushing. This is the procedure that survived contact with a real
review — two P2 findings, four wrong versions of a test file, and one commit
that still cannot be compiled here.

---

## 1. Establish what you cannot run, before you write anything

```bash
go version                      # local Go, unrelated to the target's CI pin
go vet ./cmd/gortex/ 2>&1 | head -5
go test ./cmd/gortex/ 2>&1 | head -20
```

On this host and project:

```
# github.com/zetareticule/forest: build constraints exclude all Go files
198 build-constraint exclusions from the cgo go-sitter-forest bindings
```

That is not "the tests fail". **No test can be compiled**, so a local `go test`
result is not evidence in either direction, and reporting it as such misleads
the reviewer. Say which of the three it is: *tests failed*, *tests could not be
built*, or *tests were not attempted*.

The two signals you **do** have, and they are cheap:

```bash
gofmt -l $(git diff --name-only)     # empty means formatted
go vet ./cmd/gortex/ 2>&1 | grep -v 'build constraints exclude'   # only YOUR errors
```

`go vet` **still type-checks your files** even when the package cannot be
linked against the excluded cgo tree. Zero errors from your files, filtered
past the exclusions, is a real result — narrow, but real.

> **Filter rule:** if you filter `go vet` output, run it **unfiltered** first
> and look at every line. Filtering before reading hides the one error that
> was yours.

---

## 2. Copy the functions verbatim into a harness — do not re-type them

The error that makes a harness worthless is a paraphrase. Copy the function
bodies out of the file with no edits:

```bash
# extract, do not type
sed -n '/^func newDoctorRootRedactor/,/^}/p' cmd/gortex/doctor_root_redact.go > /tmp/h/redact.go
```

Then write only the `main` and the fixtures by hand. If you find yourself
adjusting a copied line to make it compile, you have changed the thing under
test — copy the missing dependency instead.

**Harness shape that works for two-sided proof:**

```
/tmp/h/
  fixed/      <- copy of the functions AFTER the fix
  unfixed/    <- same files, `git show <base>:<path>` bodies
  main.go     <- fixtures + assertions, one file, run once per variant
```

```bash
mkdir -p /tmp/h/fixed /tmp/h/unfixed
git show HEAD:cmd/gortex/doctor_root_redact.go     > /tmp/h/fixed/x.go
git show 4a31f7a3e:cmd/gortex/doctor_root_redact.go > /tmp/h/unfixed/x.go
```

Requires `TMPDIR` on an exec-capable path — `/tmp` here is `noexec`, so build
output goes elsewhere:

```bash
export TMPDIR=/home/node/.cache/tmp-exec
GOCACHE=$TMPDIR/gocache go run /tmp/h/main.go fixed
GOCACHE=$TMPDIR/gocache go run /tmp/h/main.go unfixed
```

---

## 3. Write the assertion so it can only pass after the fix

Each check must have an input the **premise** of the old code excludes. For
the redaction finding, the premise was "paths outside repo and home are not
ours":

```go
mustEqual("sibling home root", redact("/srv/other-user/checkout-a"), "<root-1>")
mustEqual("unrelated mount",   redact("/mnt/data/repos/thing"),  "<root-1>")
```

For the classification finding, the premise was "not cli_track or mcp_track":

```go
mustTrue("project_membership alone is known provenance", !isUnattributed(set{"project_membership"}))
mustTrue("manual_config + membership", !isUnattributed(set{"manual_config", "project_membership"}))
mustTrue("only manual_config is unattributed", isUnattributed(set{"manual_config"}))
```

| variant | result |
|---|---|
| post-fix | **17 / 17 pass** |
| pre-fix | **4 failures** — 2 roots leaked verbatim, 2 intent sets mislabelled |

**The pre-fix run is the deliverable.** A harness that is 17/17 on both
variants has tested the fixtures, not the fix. Put both counts in the PR reply
so the reviewer can see the failures were aimed at their finding.

---

## 4. Writing Go through a shell heredoc — the four ways it breaks

Go source through `cat <<'EOF'` mangled the test file **four** times in one
session, each caught by a different cheap check:

| corruption | caught by |
|---|---|
| backticks inside a backtick-quoted literal | `gofmt -l` |
| missing closing brace | `gofmt -l` |
| format string split across a real newline | `gofmt -l` |
| raw string written where an interpreted one was meant | `go vet` where it applies; otherwise the **behavioural** fixture — the pattern compiles and matches nothing |

None of them was caught by a compiler, because there is no compiler for this
package here. The habit that saved the push:

```bash
gofmt -l $(git diff --name-only | grep '\.go$')
git status --porcelain
```

If `gofmt -l` names a file you did not touch, it is **pre-existing upstream** —
compare against `git status` before reformatting it, or you will ship an
unrelated diff.

**Rule: any generated `.go` file gets `gofmt -l` before it gets read.** Go is
one of the few languages where every corruption above is a formatting error,
so the formatter is a stronger syntax check than it is in Python or JS.

---

## 5. What to report, precisely

In the PR reply, three lines and no prose padding:

1. **What could not run and why** — `go test` excluded 198 cgo files; no test
   in this package was compiled here.
2. **What did run** — `gofmt -l` empty on 5 changed files; `go vet` zero errors
   from those files beyond the exclusions; harness **17/17**.
3. **What the old code did** — harness **4 failures** on the same fixtures.

Do not describe the harness as "the tests pass". It is not the suite, it does
not cover the callers, and a maintainer reading "tests pass" will check the CI
and find nothing ran.

---

## See also

- `prompts/the-count-that-proves-it-works-is-the-count-that-fails.md` — the
  general rule this procedure operationalises.
- `prompts/a-compiler-you-cannot-install-is-still-a-compiler-you-can-verify-with.md`
  — building the target *is* possible on this host via `zig cc`; this guide
  covers the case where the harness is the cheaper path.
- `tools/go-cgo-zig-toolchain-guide.md` — the build attempt, in full.
