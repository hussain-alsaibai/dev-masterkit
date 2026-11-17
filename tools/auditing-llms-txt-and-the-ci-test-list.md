# Auditing `llms.txt` and the CI test list

**Verified:** 2026-11-17, from `tiny-cli` 1.3.2, `tiny-validator` 0.7.2, `tiny-config`
0.4.2. Everything here was run against those three repos in this session; the counters are
the numbers those runs printed.

---

## Why `llms.txt` needs its own guard

Every other documentation defect is found by a human reading the wrong paragraph. An
`llms.txt` defect is found by a **model deciding not to use the library**, silently, and
the repo never learns. The file is also written from memory, in one sitting, and is the
only place in a repo where the advertised surface is a hand-typed list.

Two things make it worse than a README:

- It is the **first** file an agent reads, so a missing symbol reads as "this library
  cannot do X" rather than "this doc is stale".
- Its snippets are copied verbatim, and a snippet with a typo in a decorator produces an
  error on line 1 of the user's file, which the user attributes to the library.

## The three-part guard

`test_llms_drift.py`, in the repo's own test directory so CI runs it.

### 1. Three-way version equality

```python
doc  = re.search(r"^Version:\s*(\S+)", llms_txt, re.M).group(1)
toml = tomllib.load(open("pyproject.toml", "rb"))["project"]["version"]
mod  = importlib.import_module(PKG).__version__
assert doc == toml == mod
```

Three-way, not two-way. The pair that drifts is rarely the pair you would guess:
`pyproject.toml` is bumped by the release process, `__version__` by the author, and the
doc by neither.

### 2. Bidirectional API list

```python
DOCUMENTED_API = ["App", "run", "from_module", "command_from", "Progress", ...]

def test_every_documented_name_is_exported():
    for name in DOCUMENTED_API:
        assert hasattr(pkg, name), f"{name} documented but not exported"

def test_every_public_name_is_documented():
    for name in pkg.__all__:
        assert name in llms_txt, f"{name} exported but not in llms.txt"
```

The second direction is the one that gets skipped, and it is the one that catches a
**rename**. A forward-only check stays green forever while the doc names a symbol that no
longer exists. In `tiny-validator` the reverse direction is what surfaced the export path
(`to_json_schema`, `from_json_schema`, `to_openapi_schema`) — six names that were the
entire reason to pick the library and appeared nowhere in the doc.

Where `__all__` is not maintained, the guard list is written per repo and lives next to
the test. Do **not** try to compute it from a directory walk: modules such as
`tiny_router_sse` are part of the surface but not exported from the package root, and a
walk over-fires.

### 3. Execute the snippets

```python
SNIPPETS = re.findall(r"```python\n(.*?)```", llms_txt, re.S)

@pytest.mark.parametrize("i,src", enumerate(SNIPPETS))
def test_snippet_runs(i, src, tmp_path):
    (tmp_path / "main.py").write_text(src)
    r = subprocess.run([sys.executable, "main.py"], cwd=tmp_path,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
```

Run in a temp dir on the installed package, not on the source tree — an import that only
works because `./tiny_cli` shadows the installed one proves nothing.

Measured against the previous files: **15 failures** (`tiny-cli`), **22**
(`tiny-validator`), **20** (`tiny-config`). The `tiny-cli` total includes the snippet that
raised `AttributeError: 'App' object has no attribute 'option'` — `option` is a marker, not
a decorator.

## The CI test-list audit

A workflow that names test files by hand is a second source of truth, and the two copies
drift in exactly the direction that is silent.

```bash
# both directions; neither alone is enough
grep -oE 'tests/[a-z0-9_]+\.py' .github/workflows/ci.yml | sort -u > /tmp/named
ls tests/test_*.py | sort > /tmp/present
echo "-- present, never named:"; comm -13 /tmp/named /tmp/present
echo "-- named, does not exist:"; comm -23 /tmp/named /tmp/present
```

Findings in this session: `tiny-validator` never ran `test_v070_export_roundtrip.py`
(14 tests, written for 0.7.2) and `tiny-config` never ran
`test_v042_secret_heuristic.py` (9 tests, written for 0.4.2). Both files guard exactly the
defect class their release fixed. Nothing failed: the workflow was green, the file was in
the tree, the PR showed tests added.

Prefer plain collection (`pytest tests/`) where possible — one source of truth. Keep an
explicit list only where a file must be excluded, and write the exclusion down.

## Order of operations

1. Run the drift guard against the **current** file first and record the failure count.
   That number is the only proof the guard would have caught anything.
2. Rewrite the doc.
3. Re-run; the count goes to zero.
4. Only then add the guard to CI — a guard added before it has ever failed is untested.

## What is still not covered

Four maintained repos have no `Version:` header at all in `llms.txt` (`snapdb`,
`fast-cache`, `tiny-router`, `tiny-log`). Each has a different top-level API, so each needs
its own `DOCUMENTED_API` list. This is per-repo work, not a copy-paste, and a generic
guard would be another document claiming a coverage it does not have.

Last verified 2026-11-17 (all counters from runs in this session; the three guard files are
35, 60 and 49 tests).
