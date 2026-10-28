# A PyPI Name Collision Is a Silent Success

**A rule for every README, guide, badge, or chat message that tells someone
how to install a package you have not published yourself.**

> Found 2026-10-28. A sweep of all 62 package names in the tiny-* stack against
> PyPI found **5 genuine name collisions**. Two of them were in the in-scope
> READMEs, and the install line read `pip install tiny-router` and
> `pip install tiny-cli`. **Both commands succeed.** They install a different
> developer's package. **Last verified:** 2026-10-28 — all five collisions
> re-confirmed against the live PyPI JSON API, and a re-audit of every
> `pypi.org/project/` reference across the estate returns zero foreign or
> missing targets.

## The five collisions, confirmed live

| our package | who owns the PyPI name | their version | their project |
|---|---|---|---|
| `tiny-router` | nekonoshiri | 0.0.8 | github.com/nekonoshiri/tiny-router (a different HTTP router) |
| `tiny-cli` | TinyBio LLC | 0.1.0 | github.com/tinybio-cloud/tiny (a genomic tooling CLI) |
| `tiny-eval` | — | 0.5.0 | "TinyEval: A tiny evaluation framework for language models" |
| `tiny-memo` | meng | 1.1.6 | "A memo/note-taking application with local storage and optional blockchain features" |
| `tiny-diff` | — | 0.1.0 | "Hackable implementation of diffusion models" |

Note what the summaries say. Our `tiny-eval` is a *zero-dependency agent
evaluation framework*; theirs is a *different* TinyEval. Our `tiny-diff` is a
text diff/patch/merge library; theirs is **diffusion models**. Two of these
share a vocabulary, which is exactly what makes the collision dangerous:
**a reader who checks the name and sees a matching description still gets the
wrong package.**

## Why this is the worst bug shape

Compare the three failure modes:

| failure | visible? |
|---|---|
| `pip install tiny-nonexistent` | ✅ fails loudly: *No matching distribution found* |
| `pip install tiny-router` | ❌ **succeeds, and installs someone else's code** |
| `pip install tiny-router` then `import tiny_router` | ❌ succeeds, and you are running another project's router |

**No error, no log line, no metric.** The install works. The badge works. The
only symptom is that the library does not do what the README says, at runtime,
minutes later, in someone else's project.

The npm equivalent is already documented in
`prompts/npm-name-ownership-before-install.md` — `context-bridge` on npm
belongs to `memo-cn`, and we had never published to npm at all.

## The badge is nearly as bad

Three of the five carried a PyPI version badge pointing at the **foreign**
package. The badge rendered a version number that was not this project's
version:

```markdown
![version](https://img.shields.io/pypi/v/tiny-eval)
```

A reader sees a version badge and concludes the project is released and
maintained. The badge is a **claim about a different project**.

> **A badge rendering another project's version number is nearly as bad as no
> badge at all.**

## The check, in one request

```bash
curl -s https://pypi.org/pypi/<name>/json | python3 -c '
import sys, json
d = json.load(sys.stdin)          # raises if the name does not exist
i = d["info"]
print("name:   ", i.get("name"))
print("author: ", i.get("author") or i.get("maintainer"))
print("version:", i.get("version"))
print("summary:", (i.get("summary") or "")[:120])
print("urls:   ", list((i.get("project_urls") or {}).items())[:3])
'
```

A `KeyError`/`JSONDecodeError` means the name is **free** — that is the good
outcome. A successful response means **someone else owns it** until proven
otherwise.

## The fix that does not depend on a token

Installing from the repository URL works for every reader and needs no PyPI
account, no token, and no release process:

```bash
pip install "git+https://github.com/hussain-alsaibai/tiny-router.git"
```

For a collision case, **say why** in the README, so the next reader does not
"fix" it back:

```markdown
## Install

```bash
pip install "git+https://github.com/hussain-alsaibai/tiny-cli.git"
```

> **The PyPI name `tiny-cli` belongs to TinyBio LLC** (a genomic tooling CLI).
> `pip install tiny-cli` installs that package, not this one. This project is
> not published to PyPI.
```

The same text goes in the badge target — point the badge at the GitHub
install, not at `pypi.org/project/<name>`.

## The procedure

1. **Enumerate every name** you tell people to install. Not just the ones you
   remember publishing.
2. **Query the registry for each one.** One request each. Record the owner,
   the version, and the summary.
3. **Compare the summary to your project.** A matching name is not enough; a
   *matching description* is what makes the collision plausible.
4. **Fix every install line and every badge** in the same pass. A half-fixed
   estate still sends readers to the wrong package.
5. **Re-audit after every release.** Names get claimed by other people over
   time.

## What this does not solve

The README fix **routes around** the collision. It does not resolve it.

Publishing under a different name does resolve it, and that needs a PyPI token.
**As of 2026-10-28 there is still no PyPI credential available** — no
`~/.pypirc`, no `TWINE_PASSWORD`, no keyring entry — so the five collision
names cannot be published under their current names at all. That is a naming
decision, not a token problem.

One name is already ours and has an upgrade path: **`pysnapdb` is on PyPI at
v0.14.0 while the repo is at v0.18.0.** The other 57 names in the stack are
free.

## The generalisation

> **A `pip install` line in a README is a promise that the name on PyPI is
> yours. It is not enough for the command to work — it has to install *your*
> library.**

The command succeeding is not the check. **The command installing the right
thing is the check.**

See also `prompts/npm-name-ownership-before-install.md`,
`prompts/readme-claims-must-be-runnable.md`.
