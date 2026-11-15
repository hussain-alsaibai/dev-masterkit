---
name: a-redactors-escape-hatch-is-a-leak-when-the-scope-is-broader.md
description: Use when auditing or writing a redaction, masking, anonymising, or report-sanitising routine — the common shape "paths under my roots get rewritten, everything else passes through" silently leaks every path the report did not itself introduce.
---

# A redactor's escape hatch is a leak when the scope is broader than the report

## The prompt

> Read the branch of the redaction function that does nothing. It is always
> justified by a sentence about the data you were thinking of. Find the data
> that sentence is not about, and check whether it reaches that branch.

## What happened

`gortex` PR #1418, finding P2-4. `doctorPath` in the legacy-state census
rewrote paths under the repo root to `<repo>/...`, under home to `~/...`, and
returned everything else verbatim, documented as:

> outside both roots: no name of ours to leak

That reasoning is about the paths **the report introduced**. The census is not
that report. It is **daemon-wide**: it enumerates checkouts across the whole
machine, and a checkout root can live in a sibling home directory, on another
mount, or outside home entirely. Those came out verbatim, in both the JSON and
the human output, under `--redact`. The reviewer reproduced it through the real
collector and the real redactor, not through a unit stub.

**Fix:** a second redactor for the census (`newDoctorRootRedactor`), which
replaces every reported root with a stable per-run alias `<root-N>` wherever it
lives. It is installed through its own seam (`doctorRoot`) next to
`doctorPath`/`doctorLabel`, so it applies only under `--redact` and does not
change non-redacted output. The alias is **ordinal**, not derived from the path,
so it leaks neither the length nor the shape of the original.

## The rule

**A pass-through branch is a leak if the input set is wider than the set the
branch was reasoned about.** "Not under my roots, so it is not mine" is true for
paths the report synthesised. It is false for paths the report **observed**.

Three checks before shipping a redactor:

1. **Enumerate the input domain, not the document.** Where does this data come
   from, and is the scan wider than the report? A census, a directory walk, a
   process list, an environment dump and an index all produce data the report
   did not author.
2. **Find the unrewritten tail.** Any `return input` / `default: unchanged`
   branch is the leak surface. Assert on it with an input that is real and
   outside the assumed roots.
3. **Make the replacement structure-hiding.** An alias that encodes the path
   (`~/rep_<n>`, basename, hash of the path) is still a disclosure if it can be
   correlated. Ordinal aliases reveal order and count only.

## How to verify it

Do not verify a redactor by reading its output for paths you expected. Build a
negative control with an input the redactor's premise excludes:

```
input:  /srv/other-user/checkout-a     # real, outside repo and home
before: /srv/other-user/checkout-a     # verbatim -> leak
after:  <root-1>
```

Then re-run the fixture against the **unfixed** function and confirm it fails.
A redaction test that passes on both versions has not been aimed at the branch
that leaks.

## Where this connects

- `prompts/silent-security-control-audit.md` — a control that cannot fail does
  not exist. This is the redaction-shaped instance.
- `prompts/silent-failure-detection.md` — the pass-through is a silent failure
  with a comment explaining why it is fine.

---

**Last verified:** 2026-11-15 — reproduced by the `gortex` maintainer through
the real collector; fixed on `doctor-legacy-state` (`e1185a5a0`), PR #1418
MERGEABLE. Harness run post-fix 17/17, pre-fix 4 failures (2 roots leaked, 2
intent sets mislabelled). `go test` cannot run here (198 cgo build-constraint
exclusions); verification was `gofmt` clean on 5 changed files plus
`go vet` with zero errors beyond those exclusions.
