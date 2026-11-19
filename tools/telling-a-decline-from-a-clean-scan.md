# Telling a decline from a clean scan

**Last verified: 2026-11-19** — the probe below ran in this container on
`go1.27.3` against `go-enry` **v2.9.6** and printed the four rows in the table.
The Bearer allow-list was read from the GitHub contents API (`?ref=main`), not
from a clone.

## The 60-second probe

Put this in an empty directory and run `go run .`. It downloads one module and
answers the question "which language does the classifier assign to this
filename?" — which is the only thing a dispatcher keys on.

```
probe/go.mod
  module probe

  go 1.21

probe/main.go
  package main

  import (
      "fmt"
      enry "github.com/go-enry/go-enry/v2"
  )

  func main() {
      content := []byte(`<?php echo $_GET['x']; ?>`)
      for _, name := range []string{"vuln.phtml", "vuln.php", "a.html", "b.inc"} {
          fmt.Printf("%-12s %q\n", name, enry.GetLanguage(name, content))
      }
  }
```

Observed output (this host, 2026-11-19):

```
vuln.phtml   "HTML+PHP"
vuln.php     "PHP"
a.html       "HTML"
b.inc        "PHP"
```

Note `b.inc` is also `PHP` — the vocabulary is not extension-shaped, which is the
whole point. A `.phtml` file therefore matches **neither** a `"PHP"` allow-list
nor a `.php`-suffix check.

## Reading a scanner's allow-list

For any tool that dispatches on a classifier, find the allow-list and compare it
to the classifier's vocabulary, not to a list of extensions:

```bash
# Go tools using go-enry
grep -rn "EnryLanguages\|GetLanguage(" --include=*.go . | head

# Bearer specifically
gh api "repos/Bearer/bearer/contents/pkg/languages/php/php.go?ref=main" \
  -q .content | base64 -d | grep -A2 EnryLanguages
```

The interesting question is never "does it scan PHP?" (it does, `a.php` proves
it). It is **"what does it return for the files it declines?"**

## Making the decline visible

A scanner's clean run and its decline run produce identical output. Add the one
counter that separates them:

```go
skipped := map[string]int{}
...
if !slices.Contains(scanner.language.EnryLanguages(), fileInfo.Language) {
    skipped[fileInfo.Language]++
    return nil, nil, nil
}
...
fmt.Fprintf(os.Stderr, "skipped languages: %v\n", skipped)
```

Two rules for using it:

- **A skipped count of 0 is not proof of coverage.** It proves nothing in *that
  tree* was declined; it says nothing about the file you were asked about.
- **Print it on success, not behind `-v`.** The failure mode is a green run; a
  counter only visible in debug output will never be read on a green run.

## What NOT to do

- **Do not add the extension only.** `if strings.HasSuffix(path, ".phtml")` fixes
  `.phtml` and leaves `.pht`, `.phps` and template engines in the same hole. The
  classifier already returns the right name; use it.
- **Do not widen the allow-list to every HTML variant.** `HTML+PHP` is correct
  because the implementation can parse embedded PHP; `HTML` alone is not, and
  adding it makes the scanner parse plain markup with the PHP tree-sitter.
- **Do not treat "no findings" from a declined file as evidence of safety.**
  Running the scanner twice on a green report proves nothing. Drop a
  hand-written vulnerable fixture with the alternate extension into a scratch
  tree and confirm a finding appears; if it does not, you have found the decline,
  not a clean file.

## Where this bites in practice

- SAST tools and secret scanners that only claim one name per implementation
  (`.phtml`, `.hbs`, `.erb`, `.vue`, `.svelte` mixed-content files).
- Test runners with `testmatch` globs (`**/*.test.js` misses `**/*.spec.mjs`).
- Formatters and linters with `include` lists that were written from the
  repository's directory names.
- Coverage tools that report "100%" over files they never loaded.
