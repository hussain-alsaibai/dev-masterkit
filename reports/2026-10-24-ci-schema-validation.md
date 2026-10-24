# 2026-10-24 — The Workflow File Was Never Running

**A GitHub Actions workflow with a single wrong key does not fail a step. It
fails to load.** The file is rejected whole, the job never starts, and the
badge says "invalid workflow file" — a message that points at YAML, not at the
one token that was wrong.

This report records the fix, the verification method, and the rule that came
out of it.

## The defect

Six repos carried the same typo in `.github/workflows/ci.yml`:

```yaml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        continue_on_error: true     # NOT a GitHub Actions key
```

The real key is `continue-on-error` (hyphens). `continue_on_error` is Python
snake_case, and GitHub Actions keys are kebab-case. GitHub cannot parse the
file, so it never created a workflow run at all.

Affected (all fixed 2026-10-24, 13:20 ET):

| Repo | Local path | Commit |
|------|-----------|--------|
| `tiny-agent-memory` | `tiny-agent-memory/` | `093a803` |
| `tiny-llm` | `tiny-llm/` | `be6bad0` |
| `tiny-store` | `tiny-store/` | `7090dd3` |
| `tiny-mcp-observability` | `tiny-mcp-observability/` | `48a0f81` |
| `tiny-sandbox` | `repos/tiny-sandbox/` | `3a99d4e` |
| `tiny-workflow` | `repos/tiny-workflow/` | `28c6c46` |

A seventh repo (`tiny-safeexec`, `4f40259`) had a **different** CI failure —
ruff findings blocking the Lint step — which is a step-level failure rather
than a parse failure. Fixed the same day.

## Why a unit test did not catch this

The repos had working test suites. `tiny-agent-memory` has **50 passing
tests**. The suite was never the problem; the suite was never *run by CI*.

This is the sharpest instance yet of the pattern the 2026-10-22 and 2026-10-23
audits found: **a badge is a claim about a pipeline, not about the code.**

- 2026-10-22: `tiny-mcp-observability` had no test file and its CI ran
  `pytest tiny_mcp_observability.py` -> 0 items collected, exit 5.
- 2026-10-23: `tiny-mcp-registry` / `fast-cache` had suites whose CI target
  named only some of the files.
- 2026-10-24: six workflow files did not parse at all.

Three runs, three mechanisms, one cause: **the thing that would have checked
the claim did not exist or did not run.**

## The verification method (reusable)

The official GitHub Actions JSON Schema validates a workflow file the same way
the server does:

```bash
curl -sL -o /tmp/gh-workflow.json https://json.schemastore.org/github-workflow.json
```

Then, per file:

```python
import json, yaml
from jsonschema import Draft7Validator

schema = json.load(open('/tmp/gh-workflow.json'))
v = Draft7Validator(schema)

def norm(d):
    # YAML 1.1 parses the bare key `on:` as the boolean True.
    # The schema wants the string "on". Normalise before validating.
    if isinstance(d, dict):
        return {('on' if k is True else k): norm(v) for k, v in d.items()}
    if isinstance(d, list):
        return [norm(x) for x in d]
    return d

doc = norm(yaml.safe_load(open(path)))
errors = list(v.iter_errors(doc))
```

**The `on:` -> `True` normalisation is mandatory.** Without it every workflow
in the world reports two spurious errors:

```
[] Additional properties are not allowed ('true' was unexpected)
[] 'on' is a required property
```

On the first pass this script flagged all **204** workflow files in the
workspace as broken, including 44 of ours — all false positives from the
YAML 1.1 boolean quirk. After normalisation: **0 real errors across our 44
files.**

### Proof the check catches the actual bug

A minimal reproduction, both spellings, same validator:

| File | Result |
|------|--------|
| `continue_on_error: true` | **REJECTED** — `path=['jobs','test']` |
| `continue-on-error: true` | **PASS** |

So the schema is not a generic YAML lint. It catches the specific key
misnaming that GitHub itself rejects.

## Measured result

- Workflow files in the workspace: 204
- Our repos' workflow files: **44**
- Real schema errors in our 44 after the fix: **0**
- `continue_on_error` occurrences remaining anywhere in the workspace: **0**
- Ruff-clean repos after the 2026-10-24 fixes: `tiny-agent-memory`,
  `tiny-llm`, `tiny-store`, `tiny-mcp-observability`, `tiny-safeexec`,
  `tiny-sandbox`, `tiny-workflow` (7)
- Test suites re-verified by run after the fixes: `tiny-agent-memory` 50,
  `tiny-llm` 18, `tiny-store` 21, `tiny-mcp-observability` 35,
  `tiny-safeexec` 35, `tiny-sandbox` 35, `tiny-workflow` 56 — **all passing**

## The rule

> **A CI workflow file is an artifact that must be validated like code, not
> like prose.** It is a schema-bearing document that GitHub parses with a
> strict, undocumented vocabulary. A typo does not fail a test; it removes
> the test from existence.

Concretely:

1. **Validate workflow files against the official schema in CI.** It is one
   `curl` and one `pip install jsonschema`. Cheaper than the outage it
   prevents.
2. **A red badge whose message names the file is a different failure from a
   red badge whose message names a step.** Read the message before reading
   the code. "Invalid workflow file" never reaches your code.
3. **The fix for a parse failure is never to touch the test.** The file was
   never parsed, so it was never run, so it cannot have failed.

## Caveats

- The schema is SchemaStore's mirror of the Actions vocabulary, not GitHub's
  own file. It agrees with GitHub on the `continue-on-error` case (proven
  above) but is not guaranteed to be exhaustive.
- Only workflows under our own repos were validated. The 160 others in the
  workspace (bounty-hunting checkouts, `tscircuit`, `joblib`, `tlsx`) were
  excluded deliberately — they are not ours to fix.
- This run **could not** push anything. GitHub auth has been dead for ~36
  days; all four credential paths return HTTP 401. See the daily update.

**Last verified:** 2026-10-24 14:45 EDT
