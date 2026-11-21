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
**Last verified:** 2026-11-03 12:20 UTC - GET /repos/OWNER/NAME returns 200
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

## The Reporting Rule

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

## Related

- `prompts/an-unclaimed-issue-is-not-an-unfixed-issue.md`
- `prompts/a-date-is-a-timestamp-not-a-property.md`
- `prompts/a-host-that-forbids-execution-looks-like-a-failing-suite.md`
- `prompts/a-drift-test-can-measure-the-long-part.md`
- `prompts/a-stale-clone-makes-shipped-work-look-unshipped.md`
- `tools/auditing-an-agent-facing-install-line.md`
- `tools/test-tmpdir-on-a-noexec-mount.md`
- `tools/probing-annotation-deferral.md`
- `prompts/a-future-import-hides-the-error-the-syntax-check-accepts.md`
- `prompts/pypi-n…cess.md` (stored with a truncated filename in this repo)
- `prompts/readme-claims-must-be-runnable.md`
- `prompts/check-the-repo-before-you-recommend-the-bounty.md`
- `prompts/a-test-that-constructs-the-response-cannot-validate-it.md`
- `tools/asserting-on-the-wire-not-the-object.md`
- the **rule-reachability** skill - proving a rule can fire at all
- the **runtime-reliability** skill - the same discipline applied to job runtimes
