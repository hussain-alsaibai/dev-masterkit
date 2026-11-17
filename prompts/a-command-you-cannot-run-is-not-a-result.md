# A command you cannot run is not a result

**Discovered:** 2026-11-17 (`zzet/gortex` PR #1418, third review round, compile failure in
`cmd/gortex/doctor_legacy_test.go`)
**Last verified:** 2026-11-17 — the PR's census fixture was brace-traced with a script and
confirmed to be one `}` short, the failing form reproduces verbatim as
`vet: cannot convert "checkouts" (untyped string constant) to type int` under Go
1.27.3, and the sibling form marshals to the intended JSON; PR state read with `gh pr view
--repo zzet/gortex 1418`.

## The claim

When a package in your tree does not build on your machine, the honest thing is to say so —
and then the dishonest thing happens on its own. The limitation gets restated as a
**reason the change is fine**, the unrun command gets listed next to the ones you did run,
and the block is read as a green tick by everyone downstream, including you three rounds
later.

## What happened

`go test ./cmd/gortex/` could not run on this host: the package's test binary pulls cgo
grammar files excluded by build constraints here. The PR body said so — accurately — and
then listed:

```
go test -run 'Doctor|Legacy' ./cmd/gortex/     # ok
go test -count=1 ./cmd/gortex/                 # ok  199s
```

Neither line ever ran on that branch. The reviewer reproduced it in one attempt: the census
fixture in `doctor_legacy_test.go` nests `checkouts` **inside** the `graphs` slice, so
`"checkouts"` becomes an integer index in a `[]any` and the whole test binary fails to
build:

```
cmd/gortex/doctor_legacy_test.go:602:5: cannot convert "checkouts" (untyped string constant) to type int
```

Three review rounds. Nine findings addressed. A compile error two lines into the file that
was added to prove the fix.

## The rule

> **A comment next to a command is a claim about a run. If no terminal printed that
> command's output, it does not go in the block — it goes in the "not run" list, with the
> reason.**

Two corollaries, both learned here:

1. **"The package does not build here" is not evidence of anything about your change.** It
   is the absence of evidence. Writing it in the same list as passing runs transfers
   credibility the limitation does not have.
2. **A limitation that reproduces on the base commit exonerates the change, not the
   line.** The `./internal/indexer/` note in the same body was correct — the test binary
   exceeds RAM on the untouched tree too. The `cmd/gortex` note was not the same shape:
   that package does build here, and the file added in this PR is what broke it. Two
   sentences with the same form, one true.

## How to catch it without a buildable tree

You cannot run the command. You can run the **form** of the code in it. The failing literal
is ten lines, and it is self-contained:

```go
_, err := json.Marshal(map[string]any{
	"families": []any{map[string]any{
		"graphs": []any{map[string]any{"graph_id": "g1"},
			"checkouts": []any{ // <-- a second element of the graphs slice
				map[string]any{"checkout_id": "c1"},
			},
		},
	}}})
```

Paste it into an empty module with a `_test.go` suffix and run `go vet` there:

```console
$ go vet .
vet: ./repro_test.go:16:5: cannot convert "checkouts" (untyped string constant) to type int
```

Then move the `}` up one line — `}},` closing the graph map **and** the slice — and run it:
the JSON comes out with `checkouts` as a sibling of `graphs`, which is the shape
`indexer.FamiliesOverview` produces and the shape the test needs.

Two more steps that found the bug faster than reading:

- **Brace depth, printed.** A five-line script tracking `l.count('{') - l.count('}')` per
  line showed the fixture at depth 6 on the line that should have been back at 5. Braces
  do not need a compiler to count.
- **`gofmt -e`** parses without building. It exits non-zero on a syntax error — it does
  **not** catch this one, which is a type error, and knowing which of the two you have is
  most of the work.

## What to put in the PR body instead

| run | body |
|---|---|
| ran here, output read | the command, and the line it printed (`ok`, `143 passed`) |
| did not run, package builds elsewhere | omit, or the CI run id that did run it |
| cannot run here | the **reason**, the **base-commit comparison**, and what you ran instead |

The third row is a normal thing to write. It becomes a defect when it borrows the format of
the first row — a command, a comment, no output.

## Why it matters more for the test file than for the code

A broken production file is caught by the compiler and reported honestly. A broken **test**
file is caught by nobody on this host, is the only artifact that proves the production file,
and is the one the reviewer has to fix by hand. The PR that adds a test is the PR where
"could not run it" is most expensive — see
`prompts/a-red-test-must-fail-on-the-assertion.md`, which is the same failure with a
different cause: a test that ran but proved nothing.

## Related

- `tools/verifying-a-claim-you-cannot-execute.md` — the paste-out-the-literal procedure
- `prompts/a-red-test-must-fail-on-the-assertion.md`
- `tools/review-without-a-buildable-tree.md`
- `prompts/an-agent-facing-doc-must-be-executed-not-proofread.md`
