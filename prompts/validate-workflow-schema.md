---
name: validate-workflow-schema
description: Validate GitHub Actions workflow files against the official JSON Schema before trusting a badge, and catch key-misnaming typos that make GitHub reject the whole file. Trigger when a CI badge is red with an "invalid workflow" message, when a job reports success but the suite may not have run, or when adding or editing a .github/workflows file.
last_verified: 2026-10-24
---

# Validate Workflow Schema

## Why

A GitHub Actions workflow is **not prose**. It is a schema-bearing document
parsed with a strict, undocumented vocabulary. A wrong key does not fail a
step — it makes GitHub **reject the file**, so no job runs at all.

On 2026-10-24 six of our repos carried `continue_on_error` instead of
`continue-on-error`. One token. The repos had working test suites
(`tiny-agent-memory`: 50 passing). The suites were never the problem; **CI
never ran them.**

This is the third mechanism in three days for the same root cause:

| Date | Mechanism | Effect |
|------|-----------|--------|
| 2026-10-22 | CI ran `pytest <module>.py` (no test file) | 0 items collected, exit 5 |
| 2026-10-23 | CI target named only some test files | most of the suite invisible, badge green |
| 2026-10-24 | workflow file unparseable | **the job never existed** |

> **A badge is a claim about a pipeline, not about the code.** Never read a
> badge as evidence until the pipeline's own definition has been validated.

## Procedure

### 1. Validate against the official schema

```bash
curl -sL -o /tmp/gh-workflow.json https://json.schemastore.org/github-workflow.json
pip install jsonschema
```

```python
import json, yaml
from jsonschema import Draft7Validator

schema = json.load(open('/tmp/gh-workflow.json'))
v = Draft7Validator(schema)

def norm(d):
    # YAML 1.1 parses the bare key `on:` as the boolean True.
    # The schema wants the string "on". Normalise FIRST.
    if isinstance(d, dict):
        return {('on' if k is True else k): norm(v) for k, v in d.items()}
    if isinstance(d, list):
        return [norm(x) for x in d]
    return d

def check(path):
    doc = norm(yaml.safe_load(open(path)))
    return list(v.iter_errors(doc))

for p in sorted(Path('.github/workflows').glob('*.y*ml')):
    errs = check(p)
    if errs:
        print(p, [ (list(e.path), e.message) for e in errs ])
```

### 2. The `on:` normalisation is not optional

Skipping it flags **every** workflow in the world as broken with two
spurious errors:

```
[] Additional properties are not allowed ('true' was unexpected)
[] 'on' is a required property
```

This is not a small detail. On 2026-10-24 the un-normalised pass reported
**204 of 204** workspace workflow files as invalid — including 44 of ours that
were, in fact, clean. A validator that cries wolf on 100% of its input is
worse than no validator, because the fix for "everything is broken" is to
turn the validator off.

### 3. Prove the validator catches the bug you are fixing

Before trusting a clean result, confirm the validator rejects the known-bad
form:

```python
bad  = "continue_on_error: true"    # rejected by GitHub
good = "continue-on-error: true"
assert check_from_string(bad),  "validator is not catching the real bug"
assert not check_from_string(good)
```

A validator that passes everything is not a validator. This step is cheap and
it is the only thing that distinguishes "the check found nothing" from "the
check found nothing because it is broken".

### 4. Add the schema check to CI itself

```yaml
      - name: Validate workflow files
        run: |
          pip install jsonschema
          curl -sL -o /tmp/gh-workflow.json https://json.schemastore.org/github-workflow.json
          python -c "
          import json, yaml, pathlib
          from jsonschema import Draft7Validator
          schema = json.load(open('/tmp/gh-workflow.json'))
          v = Draft7Validator(schema)
          def norm(d):
              if isinstance(d, dict):
                  return {('on' if k is True else k): norm(x) for k, x in d.items()}
              if isinstance(d, list):
                  return [norm(x) for x in d]
              return d
          bad = 0
          for p in pathlib.Path('.github/workflows').glob('*.y*ml'):
              errs = list(v.iter_errors(norm(yaml.safe_load(open(p)))))
              if errs:
                  bad += 1
                  print(p, [e.message for e in errs])
          raise SystemExit(bad)
          "
```

Note the chicken-and-egg: this step lives in the file it validates. That is
fine — **the point is that the check runs in a workflow that GitHub accepted.**
Once one workflow per repo parses, the check can protect the rest.

## Reading the failure message

| Badge message | What it means | Where to look |
|--------------|---------------|---------------|
| "Invalid workflow file" | The file was rejected before any job ran | The workflow YAML itself |
| A named step failed | The job ran; a step failed | The step's command and its output |
| Green, but coverage looks wrong | The target may collect nothing | See `prompts/zero-tests-ran-is-a-failure.md` |

**Read the message before reading the code.** "Invalid workflow file" never
reaches your code, so no amount of debugging the module will help.

## Pitfalls

- **Never fix a parse failure by changing the test.** The file was never
  parsed, so it was never run, so it cannot have failed. Changing the test is
  how a parse failure gets converted into a silent coverage gap.
- **Do not delete the failing job.** That converts a visible failure into an
  invisible one — the same error as deleting a failing test.
- **GitHub Actions keys are kebab-case.** `continue-on-error`, `fail-fast`,
  `timeout-minutes`, `cancel-on-error`. Python-style `snake_case` is wrong,
  and it is wrong *silently*.
- **SchemaStore's schema is a mirror, not the source.** It agrees with GitHub
  on the cases proved here, but it is not guaranteed exhaustive. Treat a pass
  as "no known key errors", not as "GitHub will accept this".

## Verification

- **Last verified:** 2026-10-24
- 44 workflow files across our repos validated: **0 real errors** after the
  `on:` normalisation (204 flagged falsely without it).
- Proof case: `continue_on_error` -> REJECTED, `continue-on-error` -> PASS,
  same validator.
- 7 repos ruff-clean; 7 test suites re-verified by run, all passing.
- Full write-up: `reports/2026-10-24-ci-schema-validation.md`

## See Also

- `prompts/ci-target-must-match-repo-layout.md` — the CI target must name the real test files
- `prompts/zero-tests-ran-is-a-failure.md` — the green badge that collects nothing
- `prompts/reusable-ci-matrix-template.md` — the CI template this check belongs in
- `prompts/readme-claims-must-be-runnable.md` — the same principle applied to documentation
