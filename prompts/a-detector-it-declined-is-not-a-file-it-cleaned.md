# A detector that declined a file is not a file that was clean

**Last verified: 2026-11-19** — `Bearer/bearer` `pkg/languages/php/php.go` on `main`
declares `EnryLanguages() []string{"PHP"}` (read from the contents API at `?ref=main`
today). `go-enry` v2.9.6, run in this container on go1.27.3, reports the content
`<?php echo $_GET['x']; ?>` as:

```
vuln.phtml   "HTML+PHP"
vuln.php     "PHP"
a.html       "HTML"
b.inc        "PHP"
```

## The reading

Bearer dispatches a file into a language implementation with

```go
slices.Contains(scanner.language.EnryLanguages(), fileInfo.Language)
```

The PHP implementation claims only `PHP`. `go-enry` classifies `.phtml` as
`HTML+PHP`, so the containment test is false, `Scan` returns immediately, and
the run **reports success**. A `.phtml` template with a SQL call and a
request-derived argument produces nothing: no error, no finding, no log line.

The HTML detector already claimed `HTML+PHP`, which is why inline PHP in a
`.html` file *was* scanned. Only one extension was lost, and that is exactly the
shape of blind spot that survives for years.

## Why this is a trap

1. **"No findings" and "no file" are the same output.** The scanner's success
   path and its decline path both print a clean report. Nothing in the run
   distinguishes them, so the only detector is the one you run yourself.
2. **The allow-list is keyed on the analyzer, not on the extension.** The name in
   a language allow-list comes from the classifier's vocabulary (`HTML+PHP`),
   not from the human extension (`.phtml`). A list written from extensions
   compiles and silently under-covers.
3. **A guard that returns early is invisible to coverage.** Any test that
   asserts "the PHP detector finds this pattern" will pass against `a.php` (the
   `.php` fixtures) forever. The extension that fails is the one no fixture
   uses, so the suite is green by construction.

## The check

Ask what your tool does with the files it did **not** claim. One command answers
it for a path-based classifier:

```bash
go run .   # the probe in tools/telling-a-decline-from-a-clean-scan.md
```

For Bearer specifically, the false branch is worth a counter:

```go
if !slices.Contains(scanner.language.EnryLanguages(), fileInfo.Language) {
    return nil, nil, nil   // <- add a "skipped: <lang>" record here
}
```

A skipped-file count printed at the end of a scan is the cheapest possible
regression test for this whole class: it is a number, it must not be zero for a
file you know is in scope, and it costs one counter.

## The fix

```go
func (*implementation) EnryLanguages() []string {
	return []string{"PHP", "HTML+PHP"}
}
```

Same two-line change for any file type the implementation can genuinely parse
(`GoclocLanguages` stays `{"PHP"}` when the only purpose there is line counting).

## The general rule

**A detector that declines a file and reports nothing is the same failure mode as
a redaction that returns the input unchanged: the caller believes work happened.**
Every tool that dispatches on a classifier — linters, SAST scanners, formatters,
secret scanners, coverage tools — has a decline path that looks like a pass.
Enumerate what it declines, and emit the list.

This is the sibling of `prompts/a-test-that-constructs-the-response-cannot-validate-it.md`
one layer up: there, a green suite covered a layer it never exercised; here, a
green scan covers a file it never parsed. Both are the harness measuring at the
wrong boundary, and both are invisible from the output.

## Still owed

The two-line fix could **not** be verified in this container: there is no Go
toolchain on the pinned path for this tree's cgo dependencies (`tree-sitter`),
so `go build`/`go test` was not run against the change. The enry classification
above *was* executed (go1.27.3, `go-enry` v2.9.6, four filenames). Quote the
command, not the intention, when the PR is opened.
