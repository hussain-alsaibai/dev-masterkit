# Auditing An Agent-Facing Install Line

**Last verified:** 2026-11-20

A file written *for an agent reader* is not documentation that a human will
skim and correct. It is a list of commands that get executed verbatim, by a
reader that cannot tell "the package is not published" from "the library is
broken".

## The three-way test

Every `pip install X` line in `llms.txt` / a README quickstart / a skill file
falls into exactly one of these. Resolve it with one request:

```
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/<name>/json
```

| code | meaning | the line must say |
|---|---|---|
| **404** | unclaimed | `pip install "<name> @ git+https://github.com/<org>/<repo>.git"` |
| **200**, `author`/`project_urls` point at us | ours | the plain name works, keep it |
| **200**, someone else owns it | **squatted** | the git URL, plus an explicit "do NOT run `pip install <name>`" |

The third row is the one that gets missed. `tiny-cli` is **squatted** —
`https://pypi.org/pypi/tiny-cli/json` returns 200 and it is not ours — so its
`llms.txt` carries a warning line rather than a bare install command. That
warning is the template, not the exception; a reader that runs the short form
gets a stranger's package under a name it trusts.

## Why the README is not the thing to audit

In the 2026-11-20 fleet census, **every one of the 15 broken repos had a
correct README**: `pip install git+https://...`. The repository knew the truth,
and the file written for the agent said otherwise. If the README and `llms.txt`
agree, you have learned nothing about the install line — check the one an
agent actually reads.

## Which files to sweep

`llms.txt` is the highest-signal one, and it is also the one least covered by
tests. Sweep in this order:

1. `llms.txt` — the agent-facing digest
2. the README "Install"/"Quickstart" block
3. every `SKILL.md` `## Install` section
4. the package name in `pyproject.toml` — as a **claim to test**, never as
   evidence

## Confirming a rewrite

Do not eyeball it. `pip download` each rewritten specifier individually:

```
pip download tiny-bulkhead --no-deps
  -> ERROR: No matching distribution found for tiny-bulkhead     # before

pip download "tiny-bulkhead @ git+https://github.com/hussain-alsaibai/tiny-bulkhead.git" --no-deps
  -> Successfully downloaded tiny-bulkhead                        # after
```

`--no-deps` keeps it to one package and makes the output about the name, which
is the thing under test.

## Trap: line ranges as a proxy for semantics

A guard written as "the install line must be within N lines of the warning"
is a positional rule standing in for a semantic one. Two drafts of it failed:
a 6-line forward window reached into the next section and let a broken file
pass; moving the warning above the install line broke the files that had been
fixed correctly. Assert on the **specifier** (`git+` present, plain name
absent), not on the distance.
