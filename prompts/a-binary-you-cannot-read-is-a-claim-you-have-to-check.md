# A binary you cannot read is a claim you have to check

**Last verified:** 2026-11-10 (cleanup: this file had gone missing from the tree despite being cited by the README and `daily-updates/2026-11-06.md`; rewritten 2026-11-10 and re-verified with the wheel-inspection procedure below)

## The situation

A package's install instructions pointed at a wheel, and the wheel was a
binary — no source in the tree, no build step to read, nothing to grep. It is
tempting to treat that as "the maintainer's problem": the bytes either work or
they do not, and CI says which.

CI cannot say which. **CI tests the code the maintainer has; it does not test
the bytes a reader downloads.**

## What has to be checked, cheaply

| Claim | How it is falsified |
|---|---|
| "it installs" | install the wheel in a clean venv, `import` it |
| "it is the version it says" | `pip show` in that venv, compare to the release tag |
| "it contains the module the README imports" | list wheel contents (`unzip -l`), find the file |
| "it is not empty" | an empty wheel builds with exit 0 and holds only `dist-info` |
| "the `pip install <name>` you printed installs *your* code" | resolve the name on the index and check the owner |

The fourth row is the one that gets shipped. A build that produces no module
still exits `0`, still uploads, still installs, and still fails at first import
— often in a different repository, weeks later.

## Why a build's exit code is not evidence

`pip wheel .` and `python -m build` both exit `0` when the packaging metadata
declares a package whose module tree the build could not find. The wheel is
valid; it is validly empty.

The check that works is dull: unzip the wheel and require at least one file
outside `dist-info`/`data`. That check must have **two directions proven** —
exit `0` on a real wheel, exit `1` on a wheel rebuilt by hand to contain only
`dist-info`. A guard only ever seen passing is a guard whose failure branch
may not exist.

## The procedure

1. Build the wheel. **Inspect it before installing it.** A file count of zero
   outside metadata is a hard fail.
2. Install that specific wheel file — not the name — into a clean venv.
3. Import the module the README tells the reader to import.
4. Call one documented function and assert one documented behaviour.
5. Only then read the badge.

## The generalisable rule

> **Distribution is a separate surface from source, and it needs its own
> evidence.** Tests, CI badges and green checks all describe the tree the
> maintainer built from. The artifact a reader receives is a different object,
> built by different tooling, from a possibly different commit.

## Counter-rule

Do not re-derive this for every package in a family. Write the check once,
run it over the list, and print a per-package row. A 25-package sweep that
produces a table is worth more than one package verified by hand, because the
interesting finding is usually the *pattern* — here, that the same skeleton
had been copied 13 times with no `pyproject.toml` at all.

## Verified

- `dev-masterkit` `scripts/ecosystem_smoke.py` performs exactly this sequence
  over every advertised package: clone -> build -> **inspect wheel** ->
  install -> import. 20 tests; the empty-wheel guard is proven in both
  directions.
- Re-run 2026-11-10: PyPI returns **404** for `tiny-route-redact`,
  `tiny-mcp-audit`, `tiny-secret-mask` and `fast-cache`, so all four install
  instructions now say `pip install git+...`, verified by building and
  importing each from a fresh clone.
