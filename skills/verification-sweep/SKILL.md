---
name: verification-sweep
description: "Re-verify a family of dated or installable claims in one pass - upstream repo existence, registry name ownership, install-line safety, and guide snippet runnability - so that a wrong claim in one member exposes the method used on all of them. Use when documentation cites Last Verified dates, when a guide says pip install <name>, when a README claims a repo does not exist upstream, or before publishing a package."
---

# verification-sweep — Re-verify a whole family of claims at once

## Trigger

Use when:

- a guide says **"does not exist upstream"** / **"HTTP 404"** / **"local only"**
- a guide or README says **`pip install <name>`**
- a set of documents each carry a **"Last Verified"** date
- you are about to **publish a package** and need to know the name is free
- one member of a family turns out to be wrong

## The Core Rule

> **When one member of a family turns out wrong, the error is in the METHOD,
> not the row. Re-probe every member that shared the method.**

On 2026-11-02, two guides certified two repos as missing with
`Last Verified: 2026-11-02`. **Both repos were created on GitHub at 17:10 UTC
that same day** - after the check that signed them off. Re-probing all six
"local only" claims showed **2 of 6 still 404 and 4 were live**. The claim
was 33% true and 100% cited.


## Trap rows from 2026-11-24: a claim certified against the wrong artefact

Both defects below passed a full test suite and a "fixed" status read. Each was
found by calling the module at the boundary, not by reading a diff.

| the claim | what was actually true | the probe that would have caught it |
|---|---|---|
| `bytes_human` renders sizes correctly (140 tests green) | `1023.9999 -> "1024.0 B"` — a number that contradicts its own unit; `inf` raised `OverflowError` **inside a logging call** | one loop over `(1023.9999, 1048575.99, 0, inf)` |
| `nullable` is supported because `Field.allow_none` exists | `allow_none` was a read-only property only `Any` overrode; `fields.String(allow_none=True)` raised `TypeError`, and `required=False, default=None` **rejected every document** | construct one nullable field, validate `{}` and `{"x": None}` |
| a schema imported from JSON Schema enforces what it said | `from_json_schema` **stripped `"null"`** from `["string","null"]` and built a non-nullable field — narrower than the contract it imported | import a union-with-null, validate `None` |
| the exporter describes the validator | exporter emitted no nullability while the validator accepted nulls (fixed 0.7.4: emits `"nullable": true`) | round-trip `import(export(s))` |

**The rule these share:** a claim is certified against an **artefact**, and when
the artefact is "the suite is green" you have re-checked the cases the suite
names. Certify against the behaviour the claim is about — one call per claim,
at the boundary or the sentinel.

**Second rule: `pytest` missing from the default interpreter is not "tests
passed".** Both suites here report green only when run with an interpreter that
has pytest (`/home/node/venvs/mx-3.12/bin/python -m pytest -q` ->
140 passed / 16 skipped and 234 passed / 4 skipped). `python3 -m pytest` in this
container answers `No module named pytest`; a verification line that omits the
interpreter is indistinguishable from one that skipped the suite.

## Trap rows from 2026-11-25: who enforces it, and which path reaches it

Two defects, both green suites (143 and 196 tests), both fixed and re-measured
here. Each is a rule that was **declared** but not **enforced by the library on
the path that mattered**.

| the claim | what was actually true | the probe that would have caught it |
|---|---|---|
| `cors(allow_credentials=True)` is the incantation to allow cookies | it defaulted `allow_origins=["*"]` and **reflected the caller's `Origin`** with `Allow-Credentials: true` — a *valid* grant, so any site could read authenticated responses. Reflecting is worse than `"*"`, which browsers reject | send `Origin: https://evil.example` and read the reply headers, not the request status |
| `cors` "enforces" the Fetch rule that a wildcard cannot carry credentials | it never had to: **browsers** enforce it, by withholding the response. A library that delegates an illegal combination has not validated it | ask *who enforces this*; if the answer is the browser, the library emits no error |
| `def top(limit: int = option("--limit", default=10))` is typed `int` | `type` defaulted to `str`, so the *supplied* path gave `"5"` and the *omitted* path gave `10` — one parameter, two types, chosen by the command line; `choices=[1,2,3]` rejected its own values | call the same command twice, print `type(v).__name__` on both paths |
| the suite covers option typing | all 143 tests wrote `type=int` **explicitly** — the single spelling that could not fail | grep the tests for the *omitted* spelling; find none, then probe it |

**Third rule: name the enforcer before believing the guard.** "The library
validates X" and "X cannot be misused" are different claims. The first
requires an error at construction/parse time; the second is satisfied when a
browser, a caller, or CI catches it — silently, and only for the configurations
someone actually runs.

**Fourth rule: a default has at least two paths, and the suite names one.**
Supplied vs omitted, explicit vs implied, preflight vs simple request. Probe
both and compare **types**, not values, or the divergence reads as agreement.
See `tools/probing-both-paths-of-a-default.md`.

## The vendored snapshot that silently re-introduced a fixed defect (2026-11-25)

`repos/` holds snapshots of published packages, and a snapshot is an artefact
with its own `Last verified` claim. `repos/tiny-headers-redact` was synced on
**2026-10-15** (`3e5d620`, v0.1.0) while the live repo fixed the same file on
**2026-10-26** (`fc4acaa`). The vendored copy therefore still contained
`redact_headers()` **returning a shallow copy** when `tiny_secret_mask` could
not be imported — a security function that silently passed credentials through
and looked like it worked. Anyone reading the toolkit's copy read the defect
the live repo had already fixed.

**Fifth rule: a vendored copy is a claim, and it decays from the day it was
synced.** `Last verified` on a snapshot is the sync date, not the read date.
Before citing `repos/<pkg>` as current, `git -C ../<pkg> log --oneline -1` and
compare; a divergence means the snapshot is stale, not that the fix was
reverted.

**Sixth rule: re-sync per file, and only the files you executed.** A blind
`cp -r` of the live repo into the snapshot pulls in unrelated, unreviewed
in-flight work (here: a half-merged `.github/workflows/ci.yml` with conflict
markers, and an install-line rewrite). Copy the files whose behaviour you
probed, and leave the rest for a session that can verify them.

**Seventh rule: a docstring is part of the behaviour you are certifying.** The
fixed `redact_headers()` **raised**, but its docstring still said "falls back to
a shallow copy". The suite, the probe, and the changelog footer all agreed with
the code; only the sentence a caller reads in `help()` disagreed. Grep the
docstring for the old contract whenever you change the contract.

## Procedure

### 1. Build the family list from the documents, not from memory

```bash
cd tools/
ls *.md | sed 's/-guide\.md$//;s/\.md$//' | sort -u > /tmp/family.txt
wc -l < /tmp/family.txt
```

### 2. Extract every install line and every upstream claim

```bash
# install lines
grep -rhoE 'pip install [a-z0-9][a-z0-9._-]*' *.md \
  | awk '{print $3}' | sort -u > /tmp/names.txt

# upstream-existence claims
grep -rn -i -e 'does not exist on GitHub' \
               -e 'does not exist upstream' \
               -e 'Repo does not exist' \
               -e 'returns \*\*404\*\*' . | head -20
```

### 3. Probe GitHub, authenticated

Unauthenticated `api.github.com` calls rate-limit at ~60/hour and start
returning **403** mid-sweep, which looks like "the repo does not exist".
**That is a false negative and it will poison the whole sweep.**

```bash
# `gh api` reads the credential from the store, so no token is typed,
# exported, or embedded in the command. `--include` prints the status line.
while read g; do
  code=$(gh api "repos/OWNER/$g" --include 2>/dev/null | head -1 | awk '{print $2}')
  echo "$g -> $code"
done < /tmp/family.txt
```

A `403` in this loop means **rate limited**, not absent. Re-read it.

### 4. Probe the registry and check the OWNER, not the status code

```bash
for n in $(cat /tmp/names.txt); do
  # Download to a file FIRST, then parse the file. Never pipe a remote
  # response straight into an interpreter - that runs whatever the
  # registry returns.
  if ! curl -sSf -o "/tmp/pypi-$n.json" "https://pypi.org/pypi/$n/json" 2>/dev/null; then
    echo "$n 404"; continue
  fi
  python3 -c "
import json
i = json.load(open('/tmp/pypi-$n.json'))['info']
urls = i.get('project_urls') or {}
home = i.get('home_page') or ''
ours = 'hussain-alsaibai' in str(urls) or 'hussain-alsaibai' in home
print('$n', i.get('version'), 'OURS' if ours else 'FOREIGN',
      '|', (i.get('summary') or '')[:50])
"
done
```

**A 200 is only good if the project URLs point at your own repository.**

### 5. Fix the documents that failed

For each wrong row:

| finding | repair |
|---|---|
| repo exists upstream, guide says 404 | rewrite the Status block: state the HTTP code, the push date, the licence |
| `pip install X` resolves to **FOREIGN** | replace with the GitHub URL, and add a plain-language warning saying **whose** package owns the name and **why** the name cannot be used |
| `pip install X` returns 404 | the package is not published; say so and give the GitHub URL as the real install |

**A name that resolves to someone else's package must say so where the install
line is**, not in a footnote - a reader who runs the command will not read
the footnote.

### 6. Record the moment, not the day

For anything that can change intraday, write the **timestamp**:

```
**Last verified:** 2026-11-23 (bounty-scanner 19/19 suites green here; the farm-gate and pagination red phases reproduced by restoring `scanner.js.bak-20261123-farm-ratio`; Pypi/repo probes last executed 2026-11-03 12:20 UTC) - GET /repos/OWNER/NAME returns 200
```

A same-day re-check is a claim about the morning.

### 7. Re-run the sweep to confirm the fix

A fix that is not re-probed is a fix that is not verified.

### 8. When the claim you are checking cannot be executed, paste it out

A verification claim is usually about **one literal or one statement**, and those travel.
on 2026-11-17 a PR body listed `go test -run 'Doctor|Legacy' ./cmd/gortex/  # ok` that had
never run — the package's test binary does not build on that host. The offending construct
was ten lines of a composite literal; copied into an empty module, `go vet` printed the
exact compiler message, and the corrected form marshalled to the expected JSON.

```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=refs/pull/N/head" -q .content | base64 -d
```

Read the file from the **pushed SHA**, not from a clone that may be a rebase behind. If the
construct needs the package's own types to compile, you have not narrowed it yet.

This is the difference between *could not run* and *did not run*. Only the first is a
statement about the environment; the second is the claim you are supposed to be checking.
See `tools/verifying-a-claim-you-cannot-execute.md`.

### 7. Re-verify the two-path fix (2026-11-22)

When the claim being swept is "this defect is fixed", the defect's **shape** is
the family, not the package. Grep `is not None` used as a hit test, `if cached:`,
and `len(x)` on an optional return across every package you maintain; then check
the default branch actually contains the fix (`git ls-tree origin/main <path>`).
Run the recorded procedure in `tools/probing-a-one-path-fix.md` and quote the
red count on the previous release, not just the green count on the new one.

## ## The Reporting Rule

Report the **denominator**:

> "18 repos probed: 16 returned 200, 2 returned 404. 4 guides amended, 2
> install lines replaced with GitHub URLs."

Not: "checked the repos" and not "found some stale ones".

**A sweep that does not state how many it checked did not sweep.**

## Traps

| trap | what it looks like |
|---|---|
| unauthenticated API | `403` mid-sweep, read as "repo absent" |
| `curl -f` | the body is discarded on non-2xx, so the reason is lost (see `prompts/classify-by-status-code-not-by-reason-string.md`) |
| `pip install` succeeds | **it is not a check** - see `prompts/pypi-n…cess.md` |
| fixing one row | the method is still wrong for the other 5 |
| a date with no time | honest and stale - see `prompts/a-date-is-a-timestamp-not-a-property.md` |
| a command with `# ok` | a claim about a terminal; if you could not build it, that line in a PR body reads as a pass to everyone downstream - `prompts/a-command-you-cannot-run-is-not-a-result.md` |
| a limitation next to passing runs | "the package does not build here" is absence of evidence, and writing it in the same block as `ok` transfers credibility it does not have |
| `gofmt -e` exits 0 | it parses; a **type** error is still there - a broken fixture passed `gofmt -e` clean |
| a snippet never executed | a proposal, not a guide - see `prompts/readme-claims-must-be-runnable.md` |
| a green suite over an unobserved layer | a test that constructs the response cannot validate it; status codes were correct in 4 of 4 servers whose framing was wrong - see `prompts/a-test-that-constructs-the-response-cannot-validate-it.md` |
| "works with curl" | HTTP/1.0 endpoints frame the body by EOF, so a missing `Content-Length` is invisible until a keep-alive proxy is in front |
| a red suite on one host only | check `mount \| grep noexec` first: `/tmp` on this host is `noexec`, so a stub with mode `0o100755` fails `os.access(X_OK)` and 8 tests fail with an assertion that looks like a defect in the code under test. `TMPDIR=$HOME/tmp pytest` -> 301 passed - `prompts/a-host-that-forbids-execution-looks-like-a-failing-suite.md` |
| `chmod` returning 0 | it sets bits, it does not grant execution; only `os.access(p, os.X_OK)` or an actual `execve` proves the host will run the file |
| a drift test that passes | check **which line it asserts on**. `tiny-config`/`tiny-validator` shipped `test_llms_drift.py` green for months while asserting the version header, the Python floor and the API list - and never the install command, the one line a reader acts on. Large coverage is not placed coverage - `prompts/a-drift-test-can-measure-the-long-part.md` |
| a guard built on "the name is in `pyproject.toml`" | passed on all three broken files: the declaration is the claim under suspicion, not evidence for it. `pip install tiny-config` failed while `name = "tiny-config"` sat in the metadata - `tools/auditing-an-agent-facing-install-line.md` |
| a positional guard ("within N lines of the note") | two drafts failed: a 6-line forward window reached into the next section and let a broken file pass, and moving the note above the install line broke the files that were fixed correctly. Assert on the specifier, not the distance |
| a README that agrees | in the 2026-11-20 census all 15 broken repos had a **correct** README (`pip install git+https://...`); only the agent-facing `llms.txt` was wrong. Two files agreeing proves nothing about the third |
| 3 commits behind | a working clone reading as "the fix never landed". `repos/<name>` showed the original broken line after the fix was pushed and merged; `gh api .../contents/<path>` showed the corrected file. `git fetch` before believing any `origin/*` - `prompts/a-stale-clone-makes-shipped-work-look-unshipped.md` |

| `assignee: null` + `comments: 0` | a field check, not a work check. `openalgo` #1820 read as unclaimed on every field; its timeline carried `cross-referenced #1873`, an open PR with the same two-line fix and 107 additions. Read the timeline and the PR's **file list** - `prompts/an-unclaimed-issue-is-not-an-unfixed-issue.md` |
| a free slot inferred from a title search | PR #1873 was titled `fix: validate option offsets in order schemas`; a keyword search for "offset validator" misses it. A real bug in a contested slot still costs a maintainer a reconciliation |
| `ast.parse(..., feature_version=(3,8))` passes | it proves the file **parses**, not that it **imports**. `compile()` does not execute a module-level annotated assignment; 3.8 does. Two arms, and the failing one is the evidence - `tools/probing-annotation-deferral.md` |
| a `grep` for `dict[` as a 3.8 verdict | the same spelling is safe or fatal depending on whether `from __future__ import annotations` is present, because PEP 563 stores the annotation as a string. `tiny-cli-table` (3.7, no future import) and `tiny-secret-mask` (3.8, future import) look identical to the grep and behave in opposite ways - `prompts/a-future-import-hides-the-error-the-syntax-check-accepts.md` |
| a boolean gate returning the right answer with the wrong quote | the live replay of the issue that motivated the gate showed it quoting the comment's first line instead of the sentence that matched, and missing a hedge two sentences later. Run the gate against the **live input**, and assert on its reported evidence, not just on `null`/`not-null` - `prompts/a-gate-added-after-a-scan-has-not-been-tested-on-it.md` |
| a fix whose mtime is newer than the artifact that failed | the gate landed 3m21s *after* the scan it was written for, so that scan never exercised it. `stat -c '%y'` the fix against the scan output before calling the bug closed |
| `is not None` as a cache hit test | `None` is a value the backend is free to return; the hit test reads it as absence and re-runs the factory. `fast-cache` 0.9.0 fixed the sync path only and named only that path in its changelog - 0.9.1 found `get_or_set_async` unchanged - `prompts/a-cache-that-cannot-store-none-is-not-a-fix.md` |
| a fix merged into a non-default branch | `tiny-prompt-cache` v2 existed only on `feature/prompt-cache-v2`; the corrected code was unreachable for anyone installing the default branch. `git ls-tree origin/main <path>` answers it in one command - `tools/probing-a-one-path-fix.md` |
| a star count read from an issue record | a candidate's `stars` can be a shared/derived value, and a 61k-star repo was reported as "Repo has 0 stars". A per-repo fact must be computed once per repository, keyed by repo, never summed over issue records |
| a gate keyed on a field the adversary can buy | every farm rule keyed on `stars < 5`, so a wave that bought 33 stars and carried 329 forks passed all of them and was caught only as a side effect of `young_repo`. Add the second axis as a **ratio** (`forks >= stars * 3` at `stars >= 4`), and prove it does not fire on crewAI (61k/9k) or a 6-star/4-fork repo - `prompts/a-ratio-is-not-a-threshold-you-can-buy.md` |
| a count that shrinks between two runs of the same query | 10,209 issues at 06:09Z, 8,838 at 07:12Z, in a market that cannot shrink. Two bands lost a page to a 403 and `break`ed the pagination loop while still reporting `incomplete_bands: []` and `market_complete: true`. Diff the **per-source** counts first; confirm with `gh api -X GET 'search/issues' -f q='...' -f per_page=1 --jq .total_count` - `prompts/a-count-that-shrinks-is-a-bug-report.md` |
| `scored_count: 0` on a zero-pick day | it counts **post-gate survivors**, so "0 reached a score" was printed when 5 candidates had been scored and killed. Record `gate_counts` per population (scored / shortlisted / rejected_contested / rejected_stale / survived) and store `rejected_all` beside the `slice(0, 10)` display array, because a capped array is not an audit trail - `prompts/a-zero-pick-day-needs-a-receipt.md` |

## Related

- `prompts/an-unclaimed-issue-is-not-an-unfixed-issue.md`
- `prompts/a-date-is-a-timestamp-not-a-property.md`
- `prompts/a-host-that-forbids-execution-looks-like-a-failing-suite.md`
- `prompts/a-drift-test-can-measure-the-long-part.md`
- `prompts/a-stale-clone-makes-shipped-work-look-unshipped.md`
- `prompts/a-ratio-is-not-a-threshold-you-can-buy.md`
- `prompts/a-count-that-shrinks-is-a-bug-report.md`
- `prompts/a-zero-pick-day-needs-a-receipt.md`
- `tools/adding-a-second-axis-to-a-single-field-gate.md`
- `tools/auditing-an-agent-facing-install-line.md`
- `tools/test-tmpdir-on-a-noexec-mount.md`
- `tools/probing-annotation-deferral.md`
- `prompts/a-future-import-hides-the-error-the-syntax-check-accepts.md`
- `prompts/a-gate-added-after-a-scan-has-not-been-tested-on-it.md`
- `prompts/pypi-n…cess.md` (stored with a truncated filename in this repo)
- `prompts/readme-claims-must-be-runnable.md`
- `prompts/check-the-repo-before-you-recommend-the-bounty.md`
- `prompts/a-test-that-constructs-the-response-cannot-validate-it.md`
- `tools/asserting-on-the-wire-not-the-object.md`
- the **rule-reachability** skill - proving a rule can fire at all
- the **runtime-reliability** skill - the same discipline applied to job runtimes
