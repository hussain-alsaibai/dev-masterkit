---
title: A Red CI Badge Is A Broken Runner, Not Broken Code
tags: [ci, github-actions, fleet, python, ubuntu]
---

# A red CI badge can be a broken runner

On 2026-11-19, `ubuntu-latest` moved to **26.04**, which has no `setup-python` build of
Python 3.8 or 3.9. Every workflow whose matrix tested 3.8/3.9 on `ubuntu-latest` went red:

```
The version '3.8' with architecture 'x64' was not found for Ubuntu 26.04.
```

The rows die **in the setup step**, before a test runs. The badge is red for a reason that has
nothing to do with the code, and **56 of 137** repos in the fleet were affected.

## The rule

**Read the CI log before you change the implementation.** A failure report describes the
sample it was taken from, not the code.

The tempting fix is to drop 3.8/3.9 from the matrix. **That is the wrong fix**, and it is
wrong in the direction that ships silently: the badge goes green because you are testing
less. If `pyproject.toml` says `requires-python = ">=3.8"`, then 3.8 must still be *tested*.

The runner and the matrix are separate claims:

| claim | where it lives | how it breaks |
|---|---|---|
| the package supports 3.8 | `pyproject.toml` / `setup.py` | never, quietly |
| the suite runs on 3.8 | the CI matrix | when you trim it |
| 3.8 is installable on the runner | `runs-on:` | when the image moves |

Fix the third, not the second.

## Pinning the runner

```yaml
jobs:
  test:
    # ubuntu-latest moved to 26.04, which has no setup-python build of
    # 3.8/3.9 - those matrix rows die before a test runs.
    runs-on: ubuntu-24.04
```

Pin the image explicitly. `ubuntu-latest` is a moving target, and when it moves it moves for
every repo at once - silently, at the same moment, and only in the direction of *less*.

## The scan has to be per job

The first fleet sweep I wrote was wrong. It read `runs-on` and `python-version` from the
whole file:

```bash
grep -q 'ubuntu-latest' ci.yml && grep -q '"3.8"' ci.yml   # WRONG
```

A workflow can pin `ubuntu-24.04` for the test job and leave `ubuntu-latest` for lint, and a
file-level answer hides that. Split the workflow into job blocks and read each job's own
runner:

```python
for m in re.finditer(r'^  ([\w-]+):\s*$', text, re.M):
    block = text[m.end():next_job_start]        # THIS JOB ONLY
    runner = re.search(r'runs-on:\s*(\S+)', block)
    versions = re.search(r'python-version:\s*(\[[^\]]*\])', block)
    if versions and ('3.8' in versions.group(1) or '3.9' in versions.group(1)):
        if runner.group(1).startswith('ubuntu-latest'):
            broken.append(repo)
```

## And check the sweep was complete

The same fleet had been swept on 2026-11-15: 80 repos were pinned to `ubuntu-24.04` and the
other 56 were missed. Nothing had asked whether the sweep was finished.

**A pattern that fixed 80 repos is not finished until the other 56 get it.** Re-run the
detector after the fix, against the remote, and confirm the count went to zero. The
re-check found 56 still broken that the original sweep had missed entirely.

## Verify on the row that used to die

After the fix, prove the *specific* row works:

```
test (3.8)  Run actions/setup-python@v5  Create Python 3.8.18 folder
test (3.8)  Run tests                   28 passed in 0.03s
```

"The workflow is green" is weaker than "the 3.8 row installed 3.8.18 and ran the suite".