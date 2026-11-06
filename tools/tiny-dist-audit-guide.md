# tiny-dist-audit Guide

> **What is actually inside the file you shipped?** Deterministic release
> artifact manifests and drift detection for Python wheels, sdists and trees.
> One module, stdlib only, `>=3.9`.

**Repo:** `github.com/hussain-alsaibai/tiny-dist-audit`
**Version:** 0.1.0 (created 2026-11-06T13:05:18Z)
**Status:** **Last verified: 2026-11-06 (18:00 UTC)** — cloned fresh from
`main`, `python3 -m tiny_dist_audit --help` exit **0**, `pytest -q` **45
passed**. CI green on 3.9–3.13 plus a self-audit job that builds a real wheel.

## Commands

```
tiny-dist-audit manifest  ARTIFACT [-o OUT.json]
tiny-dist-audit check     ARTIFACT [--baseline B.json] [--key-env VAR]
                          [--fail-on info|low|medium|high|critical]
tiny-dist-audit diff      OLD.json NEW.json
tiny-dist-audit tree-digest ARTIFACT
```

- `manifest` — record file list, sizes, digests and declared modules for a
  wheel, sdist or directory tree, as stable JSON.
- `check` — compare an artifact against a baseline; **exit 1** when a finding
  at or above `--fail-on` appears. With no baseline it proves the artifact is
  *self-consistent*, which is weaker than proving it *unchanged*.
- `diff` — human-readable manifest-to-manifest comparison.
- `tree-digest` — one digest for a directory, for pinning an unpacked tree.

## The workflow that makes a comparison possible

```bash
pip wheel . -w dist --no-deps
python -m tiny_dist_audit manifest dist/*.whl -o dist/manifest.json
# next release:
python -m tiny_dist_audit check dist/*.whl \
    --baseline previous/manifest.json --fail-on high
```

Ship the manifest as a **release asset**. A manifest that lives only in CI is a
manifest the next run cannot diff against.

## What a finding means

| finding | the defect behind it |
|---|---|
| file added / removed | a module travelling inside a published wheel |
| digest moved, version unchanged | the build is not reproducible, or source moved under a tag |
| declared module missing | the sidecar bug — file in the tree, absent from `py-modules`, install falls into `except ImportError` |
| metadata differs between builds of one commit | expected; the reason a naive byte-compare is useless |

## The two CI failures it hit before green

1. The job installed the package from **PyPI** before it existed there.
2. The job called the console script with nothing installed → exit **127**.

Both were the same mistake — an artifact tested through a channel that does
not contain the code under test. Fixed by running `python -m tiny_dist_audit`
from the checkout, which is also what the self-audit job does.

## Mutation-proved

The signature guard passed **all 43 tests** in its first form. Making
`verify()` return `True` unconditionally survived the suite; only
`assert verify({}) is False` — a negative case — fails it. **A positive-only
suite proves the code runs, not that it checks.**

## Fit

Pair with `tiny-validator` (contract shape) and `tiny-mcp-contract` (server
tool-list pins). This records *what shipped*; it does not prove *which commit
it was built from* — that is provenance, a separate control.

## Census, 2026-11-06

70 `tiny-*` repos: 63 with `pyproject.toml`, 3 with `package.json`, **1**
containing an artifact manifest — this repo, created the same morning. See
`prompts/a-binary-you-cannot-read-is-a-claim-you-have-to-check.md`.
