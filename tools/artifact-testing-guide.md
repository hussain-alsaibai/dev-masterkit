# Testing a published artifact: sdist, wheel, `PKG-INFO`

**Last verified:** 2026-11-11 — commands run on snapdb 0.18.1 from this host

Everything a packaging defect can hide behind, in one page. The checkout is
the one tree that cannot show a packaging bug; the artifact is the one tree
that can.

## Build without `build`

`python3 -m build` is frequently absent (installing it needs network the sandbox
may not have). `uv` ships a builder:

```bash
uv build --sdist                 # dist/pkg-x.y.z.tar.gz
uv build                         # sdist + wheel
python3 -m build                 # only if the module exists
```

## Unpack and run the suite where the user will run it

```bash
tmp=$(mktemp -d)
tar xzf dist/pkg-*.tar.gz -C "$tmp"
cd "$tmp"/pkg-*/ && pytest -q
```

| symptom in the unpacked tree | cause |
|---|---|
| `FileNotFoundError: CHANGELOG.md` | test reads a root file `MANIFEST.in` does not ship |
| `fixture 'name' not found` (every run) | a module-level `def test(name, ...)` helper got collected |
| `ImportError: no module named pkg` | package dir not in `[tool.setuptools] packages`, or src-layout mismatch |
| passes here, fails from `pip install` | wheel-only problem (data files, entry points) |

## Read the version out of the artifact, not the repo

`PKG-INFO` is RFC-822 **without a section header**, so `configparser` raises
`MissingSectionHeaderError`:

```python
import re, pathlib
text = pathlib.Path("pkg-1.2.3/PKG-INFO").read_text()
version = re.search(r"^Version:\s*(\S+)", text, re.M).group(1)
```

Compare that against `pkg.__version__` — not against `pyproject.toml`, which
is the input to the build, not its output.

## Inspect the wheel

```bash
python3 - <<'PY'
import zipfile, sys
z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
print(len(names), "entries")
print([n for n in names if n.endswith(".so")])
print([n for n in names if n.endswith("METADATA")])
PY
```

An **empty wheel** (only `dist-info/`) builds successfully and installs
nothing. Guard: exit non-zero when the wheel carries no module files. Prove the
guard in both directions — exit 0 on a real wheel, exit 1 on one rebuilt to hold
only `dist-info`.

See also `tools/wheel-inspection-guide.md` for `SOURCES.txt` and `RECORD`
comparisons.

## Tests that exec their own fixtures need an exec-capable TMPDIR

If a suite writes a fake binary (`os.chmod(path, 0o755)`) and then runs it, a
`noexec` mount turns every case into `FAIL: ... is not an executable file` —
with the **right mode** on disk and `os.access(X_OK)` returning True.

Measured 2026-11-11 on this host: `/tmp` is `rw,nosuid,nodev,noexec`, so
`tests/test_scan_skills.py` reported **7 failed, 49 passed** using the default
tempdir and **56 passed** with `--basetemp=/home/node/ptbase`. The script under
test was correct; the mount refused to execute the fixture.

```bash
findmnt -no OPTIONS -T /tmp          # look for noexec
python3 -m pytest tests/ -q --basetemp=/home/node/ptbase
```

Do not "fix" the script or the test when the mount is the variable — re-run on
an exec-capable path first, and record the mount option in the test's docstring
so the next session does not re-derive it.
