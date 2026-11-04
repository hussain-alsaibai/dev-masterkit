# Duplicate Module Audit — 2026-11-04

**Last verified:** 2026-11-04 (18:35 UTC) — every file below was read from the
repo's **published `main`**, fetched as a GitHub tarball, not from a local clone.

**Checker:** `scripts/check_duplicate_modules.py` (new), 14 tests in
`tests/test_check_duplicate_modules.py`.

**Trigger:** the 2026-11-04 finding that `tiny-safeexec` shipped as a
byte-identical clone of `tiny-sandbox`, found by reading two files by hand. The
rule written that morning — *one fix in one repo is not a fix* — had no
mechanical check behind it. Now it does.

---

## Method

1. List every published `tiny-*` repo: **134** names, via the authenticated API.
2. Download each repo's `main` tarball (`/repos/<owner>/<name>/tarball/main`) and
   extract it into its own directory.
3. Hash every `.py` file with SHA-256, skipping `build/`, `dist/`, `.venv/`,
   `__pycache__/` and the other artefact directories.
4. Report any hash that appears under **two or more package names**.

Files under 200 bytes are skipped (empty `__init__.py`, version stubs and
licence headers match trivially and mean nothing) and so are `test_*.py` and
`conftest.py` (a shared generated test helper is not a shipped-copy defect).

**Coverage caveat, stated because it is the point:** 134 repos downloaded,
**92** carry a `pyproject.toml` and were scanned, **162** distinct modules
hashed. The other 42 either have no `pyproject.toml` or no shipped module. A
check over 92 of 134 is a check over 92 of 134.

## Result

`scanned 92 packages, 162 distinct modules >= 200 bytes` — **2 duplicate groups**.

| hash | packages | file | bytes |
|---|---|---|---|
| `2b6e2968bde3` | tiny-safeexec, tiny-sandbox | `tiny_sandbox.py` | 23,321 |
| `2171dd1daeae` | tiny-mcp-gateway, tiny-retry, tiny-task | `benchmark.py` | 684 |

The first is the copy already documented and already declared in
`tiny-safeexec`'s README H1. It is a **known, admitted** duplicate; it can be
recorded with `--ignore tiny-safeexec:tiny-sandbox` and the pair then passes.

The second is new and was not found by reading any of the three repos.

## The benchmark.py finding

Three packages ship the same 684-byte `benchmark.py`, all committed at
`2026-08-04T13:11:34Z` in the v1.0.0 initial commit of each repo:

- `tiny-retry` — `f0ba690`
- `tiny-task` — `248f44c`
- `tiny-mcp-gateway` — `c44415a`

The file is a template that was emitted with the repo name substituted in by a
`str` expression, and the substitution collapsed into a literal dict lookup
written three times. Its only runtime behaviour is a `pass` inside
`run_benchmarks()`. The module body ends with:

    if __name__ == "__main__":
        print("Run: python -m pytest benchmark.py")

Measured today, in a fresh extraction of each of the three repos:

| command | result |
|---|---|
| `python3 benchmark.py` | prints `Run: python -m pytest benchmark.py`, exit 0 |
| `python3 -m pytest benchmark.py --collect-only` | `no tests collected` |
| `python3 -m pytest benchmark.py` | **exit 5** (no tests collected) |

So the instruction the file prints is an instruction that **cannot succeed**, and
it is the only thing the file does. `tiny-retry` separately ships a working
`bench_tiny_retry.py`, so the repository's real benchmark is not this file; the
other two have no working benchmark at all.

**Not yet fixed upstream.** This report records the measurement; no PR is
attached to it. The three repos have no benchmark claim in their READMEs, so the
honest repair is either a real benchmark or deleting the stub — not rewriting the
print line.

## Rules this adds

> **A file that ships in three repos is three files, and a fix lands in one.**
> The duplicate check exists because finding a copy by reading is luck, and the
> copies that matter are the ones nobody re-reads.

> **A smoke test that exits 0 can be a stub.** `benchmark.py` exits 0 and prints
> an instruction; `pytest` on it exits 5. The exit code of the wrapper is not the
> result of the work.

> **Record the declared duplicate; do not suppress the class.** `tiny-safeexec`
> is a copy that says it is a copy, so it is `--ignore`d by name. The three-way
> benchmark copy has no such claim and is reported.
