# An agent-facing doc must be executed, not proofread

**Discovered:** 2026-11-17 (`llms.txt` in `tiny-cli`, `tiny-validator`, `tiny-config`)
**Last verified:** 2026-11-17 — 15 / 22 / 20 failures against the previous `llms.txt`
files; 35 / 60 / 49 tests in the three `test_llms_drift.py` guards, all green.

## The claim

`llms.txt` is read by a model **before** it decides whether a library can do a job, and it
is written by hand from memory. It is the one document in a repo where a stale claim
eliminates the library from consideration, and where a wrong snippet is the *first* line a
new user copies. Neither is caught by any test that reads the code.

## What the files said

| file | advertised | actual |
|---|---|---|
| `tiny-cli/llms.txt` | `Version: 1.1.0`, Python 3.8+ | 1.3.1, `>=3.9` |
| `tiny-validator/llms.txt` | `Version: 0.3.0` | 0.7.2 |

And both under-documented the library by several releases:

- **`tiny-cli`** never mentioned `from_module`, `command_from`, `Progress`, `Spinner`,
  `confirm` or `load_env`.
- **`tiny-validator`** never mentioned `Schema`, `AsyncValidator`, `to_json_schema`,
  `to_openapi_schema`, `from_json_schema` or `http_error_response` — the **export path**,
  which is the reason to pick it — and listed 9 of its 18 field types.

A reader who trusts the file concludes the library cannot do the job.

## The advertised first example did not run

```python
@cli.command(help="Add an entry")
@cli.option("--text", required=True, help="Entry body")   # AttributeError
```

`option` is a **marker**, not a decorator, and `required=` does not exist on it. The
snippet raised `AttributeError: 'App' object has no attribute 'option'` on the first line
a new user copies.

## The guard that stops it recurring

`test_llms_drift.py`, three checks, each covering a different drift:

1. **Version header = `pyproject.toml` = `__version__`.** Three-way, because any two of
   those can agree while the third drifts.
2. **API list in both directions.** Every name the docs promise must be exported; every
   name in the guard list must appear in the docs. The reverse direction is the only one
   that catches a **renamed** export — a forward-only check stays green while the doc
   names something that no longer exists.
3. **Execute the snippets.** Both repos run their documented examples as subprocesses. A
   decorator typo cannot pass step 3; a stale version string cannot pass step 1.

Proven before shipping: **15 failures** for `tiny-cli`, **22** for `tiny-validator`, **20**
for `tiny-config`, against the previous files.

## The rule

> **A documentation example is a claim about executable behaviour; execute it or delete
> it.** Three-way version equality and a bidirectional API list are the cheap half. The
> expensive half — running the snippets — is the half that finds the decorator typo.

## The side effect worth the effort

Fixing the docs found **three real bugs in `tiny-cli`** that 57 tests had passed:
`option()`'s `dest`, an option with no default being registered as optional, and a parse
error writing the usage line into the JSON envelope's stdout. All three were on the path
the documented example took, which is why the docs were wrong in the first place — the
example had never been run.

Last verified 2026-11-17 (three guards green; failure counts measured against the previous
files before the rewrite).
