# wheel-inspection — what a compiled release actually contains

**Last verified:** 2026-11-10

A small stdlib-only helper baked into `scripts/ecosystem_smoke.py` and used by
hand since: open a wheel or sdist and answer three questions before anything is
installed.

1. **Does it contain a module?** (or only `dist-info`)
2. **Which importable paths does it provide?**
3. **Are there compiled extensions** — i.e. is this a binary a reader cannot
   review?

## Why it exists

`pip wheel .` exits `0` on a validly empty wheel, and `unzip -l` is the only
thing that says so. The same tool answers "is this pure Python?" which decides
whether an install can be trusted in a scratch tmpfs directory
(`prompts/a-so-that-cannot-map-is-not-a-broken-wheel.md`).

## Usage

```bash
# module paths a wheel actually provides
python3 - <<'PY'
import zipfile, sys
z = zipfile.ZipFile(sys.argv[1] if len(sys.argv) > 1 else "dist/pkg.whl")
names = z.namelist()
paths = [n for n in names if not n.startswith(("dist-info/", "pkg-"))]
print("files outside metadata:", len(paths))
for n in paths:
    print(" ", n)
PY
```

```bash
# is it pure python, or does it carry .so files?
unzip -l dist/pkg.whl | grep -c '\.so$'
```

## Rules learned the hard way

- **Count files outside `dist-info` before installing.** Zero is a failure, not
  a small package.
- **A `.so` in the wheel means the install needs real filesystem space.**
  tmpfs with a full page cache fails `mmap` and reports "failed to map
  segment".
- **`pip install git+...` is the honest instruction when the index 404s.**
  Verified 2026-11-10: `tiny-route-redact`, `tiny-mcp-audit`,
  `tiny-secret-mask` and `fast-cache` all return **404** from
  `pypi.org/pypi/<name>/json`.

## The check is a guard, so it has two directions

`tests/test_ecosystem_smoke.py` proves the empty-wheel guard **exits 1** on a
wheel rebuilt by hand to hold only `dist-info`, and **exits 0** on a real one.
A guard exercised only on the passing case has never been shown to have a
failing branch.

## Verified

- 2026-11-10: `python3 -m pytest tests/ -q` in a fresh clone -> **48 passed**.
- `python3 scripts/check_structure.py` -> `41 total, 41 loadable, 0 pending`.
- Wheel inspection run against the four packages above; all four install from
  their git URL and import.
