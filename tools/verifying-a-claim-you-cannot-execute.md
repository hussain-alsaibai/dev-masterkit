# Verifying a claim you cannot execute

**Verified:** 2026-11-17, on `zzet/gortex` PR #1418. The failing literal was extracted from
the PR head with `gh api …?ref=refs/pull/1418/head | base64 -d`, pasted into an empty Go
module, and compiled under Go 1.27.3; the fixed form was run and its JSON output read. The
reviewer's diagnosis was published at 2026-11-17 12:06 UTC and this run reached the same
finding from the file alone.

## When to use this

- The reviewer says a file does not compile, and the package cannot build on your host.
- You wrote "could not run `X` here" in a PR body and want to know whether you were right.
- A test file was added in a tree where `go test`, `cargo test`, or the equivalent is
  excluded by build constraints, missing grammars, or RAM.

## The procedure

### 1. Get the exact file from the PR head, not from your clone

```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=refs/pull/N/head" -q .content | base64 -d > /tmp/file.go
```

Your clone may be a rebase behind; the reviewer read the pushed SHA.

### 2. Find the construct, bound its size

The claim is almost always about **one literal or one statement**, and those are
self-contained by nature. If the construct spans 300 lines and needs the package's types,
you have not found the claim yet — keep narrowing.

### 3. Paste it out into an empty module

```bash
mkdir -p /tmp/repro && cd /tmp/repro
printf 'module repro\n\ngo 1.22\n' > go.mod
# minimal decls the construct needs (here: two strings, an encoding/json import)
```

The value `go vet` reports is read from the compiler's view of that one file: the message
names the line and the type, which is the entire diagnosis.

### 4. Then apply the proposed fix and run it

A repro that fails proves the reviewer right. A fixed repro that **runs and prints the
intended output** proves the fix is the right fix, not just a silencer:

```console
$ go test -v .
=== RUN   TestFixed
    fixed_test.go:24: {"families":[{"checkouts":[...],"family_id":"fam","graphs":[...]}]}
--- PASS: TestFixed (0.00s)
```

The printed JSON is the second proof: it shows `checkouts` arriving as a **sibling** of
`graphs`, which is the shape the test needs, rather than merely "it compiles now".

### 5. State what remains unrun

The repro proves the literal. It does **not** prove the test passes against the package.
Say exactly that:

> "The literal fails to compile outside the package, and the corrected literal marshals to
> the expected shape. The package test binary was not run on this host — `<reason>`."

## Cheap precursors, in order

| check | catches | misses |
|---|---|---|
| `gofmt -l file` | formatting drift, some syntax | every type error |
| `gofmt -e` (non-zero exit) | syntax | the error here (`cannot convert … to int`) |
| brace-depth print | an unbalanced or misplaced `}` | a balanced but wrongly nested one |
| paste-out + `go vet` | **type errors** | anything the package's own types decide |
| `go build ./pkg/` | production files only | `_test.go` by construction |

The brace-depth one-liner is worth keeping, because it reads a 400-line fixture without a
compiler:

```python
depth = 0
for i, l in enumerate(src, 1):
    print(i, depth, l); depth += l.count('{') - l.count('}')
```

## The rule this serves

A line in a PR body's verification block is a claim about a terminal. When the terminal did
not exist, the honest artifact is the **reason** plus the **nearest thing you could run** —
never the command with an `# ok` after it. See
`prompts/a-command-you-cannot-run-is-not-a-result.md`.
