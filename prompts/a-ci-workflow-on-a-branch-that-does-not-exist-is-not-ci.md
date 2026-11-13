# A CI workflow on a branch that does not exist is not CI

**Last verified:** 2026-11-13 (12:00 EST) — `unzip-http`: workflow file present
since creation, `gh run list` **empty for the repo's whole life**. Trigger named
`master`; the only branch was `fix-readme-typos`.

## The rule

> **A workflow file is not a workflow. Ask whether it has ever run.**

```sh
gh run list --repo OWNER/NAME            # empty == the trigger never matched
gh api repos/OWNER/NAME/branches         # does the trigger's branch exist?
```

The local branch name is not the remote's.

## `branches:` is an allowlist, not a hint

`master` and `main` are different branches and normally only one exists. When a
repo's default branch is unusual — here a topic branch became default — every
trigger naming `main` silently never fires.

## Two more problems hiding behind it

Even on the right branch this workflow would have failed:

- `python setup.py develop` — removed from modern setuptools.
- A test step that fetched a hardcoded external ZIP over HTTP.

## `NO_CI_WORKFLOW` has two meanings

No workflow *file*, or a workflow that has never *run*. The health report said
the first; the truth was the second. Check the runs, not the file.

## What fixed it

13 tests over a local `ThreadingHTTPServer` that serves a real zip and honours
`Range` requests — deterministic, no external network, exercising the one thing
the library exists to do (fetch only the needed byte ranges). Matrix 3.8-3.13,
which is what proves the `python_requires = ">=3.8"` claim.

**Read the API before writing tests for it.** Six tests were written against a
`read()` method that does not exist; the real API is `open(fn)` returning a
stream plus `extract()` writing to disk. First suite: 6/10 failed, every failure
an assumption. `grep "def " class` first, then write the test.
