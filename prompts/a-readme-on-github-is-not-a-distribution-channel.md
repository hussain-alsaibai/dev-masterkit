# A README On GitHub Is Not A Distribution Channel

**A rule for every package that has a README, a repository, and no release
mechanism.**

> Found 2026-11-03. An audit of all **37** of our own Python packages against
> the live PyPI JSON API found **only 4 published**. **Last verified:**
> 2026-11-03 — every name re-probed against `https://pypi.org/pypi/<name>/json`
> on the day of writing.

## The Rule

> **A README is a landing page. A package index is a distribution channel.
> Only one of them installs.**

## The Measured State

| package | PyPI | consequence |
|---|---|---|
| `pysnapdb` | **200** | 13 downloads/month — ours, `github.com/hussain-alsaibai/snapdb` |
| `tiny-router` | 200 | **someone else's** — nekonoshiri's HTTP router, 8 dl/mo |
| `tiny-cli` | 200 | **someone else's** — TinyBio LLC's genomic CLI, 4 dl/mo |
| `tiny-diff` | 200 | **someone else's** — diffusion models, 4 dl/mo |
| `tiny-eval` | 200 | **someone else's** — a different TinyEval, 5 dl/mo |
| `tiny-log`, `fast-cache`, `tiny-config`, `tiny-validator`, `tiny-context`, `tiny-skill-lint`, `tiny-skill-md`, `tiny-agent`, `tiny-mcp`, `tiny-budget`, `tiny-chain`, … | **404** | **not installable by anyone** |

**33 of 37 return 404.** The four that resolve to a 200 are mostly *other
people's* packages that happen to share a name.

## Why The Gap Is Invisible From Inside The Repo

Every one of these packages has:

- a README with a usage example,
- a LICENSE,
- a `pyproject.toml`,
- a passing test suite,
- a green CI badge on GitHub.

From the repo, the package looks **published**. It is not published at all.
The difference is visible only against the registry:

```bash
# the check
curl -s -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/<name>/json
# 404 means: nobody can install this
```

**The GitHub badge proves the tests pass. It does not prove the package is
installable.** Those are two different claims and only one of them is about
distribution.

## The Two Failure Modes, Both Silent

```bash
pip install tiny-router     # SUCCEEDS -> installs nekonoshiri's router
pip install tiny-log        # FAILS loudly -> "No matching distribution found"
```

The 404 is loud, so nobody fixes it. The collision is **silent and looks like
success** - see `prompts/pypi-n…cess.md` (the file is stored with a truncated
name in this repo; the content is "A PyPI Name Collision Is a Silent
Success").

## The Procedure

1. **Probe every name against the registry, not the repo**:

```bash
for n in <every-package-name>; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/$n/json")
  echo "$n $code"
done
```

2. **Check the owner, not just the status code.** A 200 is only good if the
   `project_urls` / `home_page` points at *your* repository:

```bash
curl -s https://pypi.org/pypi/<name>/json | python3 -c "
import json,sys
i = json.load(sys.stdin)['info']
urls = i.get('project_urls') or {}
home = i.get('home_page') or ''
print('OURS' if 'hussain-alsaibai' in str(urls) or 'hussain-alsaibai' in home else 'FOREIGN')
"
```

3. **A name with no `name =` in `pyproject.toml` has no distribution name
   yet.** `tiny-agent`, `tiny-mcp` and `tiny-validator` have none - the
   intended name is still undefined, and it must be resolved **before** any
   publish attempt, not after.

4. **Publish with a workflow, not by hand.** Only `snapdb` has
   `.github/workflows/release.yml`. The other three published packages were
   pushed by hand, which is exactly why they are still at `0.1.0`.
   **A manual release process stops at the first busy week.**

5. **Pick a name that is actually searchable.** Ours ships as `pysnapdb`
   because `snapdb` on PyPI belongs to Scott Cruwys' *"Python adapter for
   SnapDB"*. `pysnapdb` gets 13 downloads a month; the search term
   `snapdb` gets somebody else's package.

## The Market Context

The category is not small: `context-mode` does ~37,976 npm downloads/week
and `@modelcontextprotocol/sdk` does 87M. **The audience exists.** What is
missing is the release mechanism, not the demand.

## The Generalisation

This is the same shape as `prompts/readme-claims-must-be-runnable.md` (the
README describes an API that does not exist) and
`prompts/a-date-is-a-timestamp-not-a-property.md` (a dated claim that has
gone stale). **A claim about a registry must be checked against the
registry.**
