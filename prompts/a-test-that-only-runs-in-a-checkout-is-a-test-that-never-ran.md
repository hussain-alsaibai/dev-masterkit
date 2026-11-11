# A test that only runs in a checkout is a test that never ran

**Discovered:** 2026-11-11 (snapdb 0.18.1, `55cc77f`)
**Last verified:** 2026-11-11 — measured from an unpacked sdist built by `uv build --sdist`

## The failure

`pytest` in the git checkout: green. `pytest` in an unpacked sdist of the same
commit: **2 failed, 2 errors**. Two independent causes, both invisible in a
checkout because a checkout has files an sdist does not:

1. `tests/test_version_consistency.py` read `CHANGELOG.md` and `package.json`
   from the repo root. Neither was in `MANIFEST.in`, so both were absent from
   the tarball → `FileNotFoundError`. The suite that exists to prove the
   published version is consistent could not run against the published bytes.
2. `tests/test_delta_encoding.py` and `tests/test_dict_encoding.py` defined a
   module-level helper `def test(name, ok, detail="")`. pytest collects it as a
   test that needs a `name` fixture → `fixture 'name' not found` on **every**
   run, including ours. 39 call sites renamed to `check()`.

## The rule

> A repository's test suite must be runnable from its own published artifact.

The checkout is the one place a packaging defect cannot appear. Test from:

```bash
uv build --sdist                       # works where `python3 -m build` is missing
tar xzf dist/*.tar.gz && cd pkg-x.y.z  # the bytes users get
pytest -q
```

## Guards that stop it recurring

- `tests/test_module_level_api.py` asserts three separate facts:
  1. the tarball contains every file the suite reads,
  2. the tarball's `PKG-INFO` version matches the package `__version__`,
  3. no test module defines a collectable `test()` helper.

Fact 3 is a five-line AST walk, and it is the one that catches the silent
half: a module-level `test()` helper does not fail once, it poisons the whole
file in a way that reads like a fixture error.

## Measure both directions

| from | result |
|---|---|
| `snapdb` 0.18.0 unpacked sdist | 2 failed + 2 errors |
| `snapdb` 0.18.1 unpacked sdist | 236 passed, 5 skipped, 0 errors |

A packaging fix that is not measured in the unpacked tree is a guess about a
tree you never opened.

## Related

- `prompts/a-binary-you-cannot-read-is-a-claim-you-have-to-check.md` — the
  artifact is a separate fact from the repo.
- `prompts/readme-claims-must-be-runnable.md` — the same shape for documented
  examples.
