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
| a snippet never executed | a proposal, not a guide - see `prompts/readme-claims-must-be-runnable.md` |

## Related

- `prompts/a-date-is-a-timestamp-not-a-property.md`
- `prompts/pypi-n…cess.md` (stored with a truncated filename in this repo)
- `prompts/readme-claims-must-be-runnable.md`
- `prompts/check-the-repo-before-you-recommend-the-bounty.md`
- the **rule-reachability** skill - proving a rule can fire at all
- the **runtime-reliability** skill - the same discipline applied to job runtimes
