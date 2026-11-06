# A Binary You Cannot Read Is A Claim You Have To Check

**A rule for anything you install as a release artifact — wheel, sdist, binary,
nightly build, RC — rather than read as source.**

> Found 2026-11-06. A census of 70 `tiny-*` repositories found **63 with a
> `pyproject.toml` and exactly 1 containing an artifact manifest** — and that
> one was the tool written the same morning to produce them (`tiny-dist-audit`,
> created 13:05Z, manifest 13:08Z). The ecosystem that documents its source
> carefully, and ships releases nobody compares against it.
> **Last verified:** 2026-11-06 (18:00 UTC) — `tiny-dist-audit` cloned fresh
> from `main`, `python3 -m tiny_dist_audit --help` exit **0**, `pytest -q`
> **45 passed**.

## The Rule

> **What a release artifact contains is a separate fact from what the repo
> says. Record it at build time, compare it per release, or you are trusting a
> filename.**

"Version 0.8.0 of the package" is not evidence. The evidence is a manifest:
file list, sizes, digests, derived at build time, checked against the previous
one. Two days ago the same class of defect was caught in version *strings*
(`prompts/a-version-guard-only-covers-the-files-it-reads.md`); this is the same
failure one layer down, where the thing that drifted is the artifact itself.

## Why it goes unnoticed

- **Nobody diffs a release.** Users install it, CI installs it, a green badge
  reports that the *tests* passed against the *checkout*.
- **Accounting bugs look like noise.** A digest that differs between parallel
  builds, a file resolved twice, a timestamp in the archive — each is
  individually ignorable and collectively means no comparison is possible.
- **The RC is the release that was never read.** `dev-1.2.0-rc.618` is a
  hundred builds apart from `dev-1.2.0` with nobody having compared them.

## The minimum that makes a comparison possible

```bash
# Build-time: record. Release-time: compare. Both are exit-coded.
pip wheel . -w dist --no-deps
python -m tiny_dist_audit manifest dist/*.whl -o dist/manifest.json
python -m tiny_dist_audit check dist/*.whl \
    --baseline previous/manifest.json --fail-on high
```

A `check` with no baseline proves the artifact is self-consistent; only a
baseline proves it is *unchanged where it should be*. Ship the manifest as a
release asset so the next run has something to diff against.

## What the check has to be able to fail on

1. **A file added or removed.** This is the one that matters — an unpublished
   module travelling inside a published wheel is invisible to every test.
2. **A digest that moved with no version change.** Either the build is not
   reproducible or the source moved under a tag.
3. **A declared module missing from the package.** The classic sidecar bug: the
   file is in the tree, absent from `py-modules`, and every install falls into
   an `except ImportError` path.
4. **Timestamps/metadata differing between two builds of one commit** — not a
   defect in itself, and the reason a naive byte-compare is useless.

## Test the checker by proving it can be fooled

`tiny-dist-audit`'s signature guard passed all 43 tests in its first form. The
mutation that exposed it: make `verify()` return `True` unconditionally. Only a
test that asserts `verify({}) is False` — a negative case, not a positive one —
can fail that. **A positive-only suite proves the code runs, not that it
checks.**

## What this does not fix

A manifest proves what was built, never that it was built from the commit it
claims. Provenance (build attestation, signed tag, rebuild-and-compare) is a
different control, and saying so plainly is cheaper than a manifest read as a
provenance record.

See also: `daily-updates/2026-11-06.md`,
`dev-tooling-trends-2026/reports/2026-11-06-verifying-release-artifacts.md`.
