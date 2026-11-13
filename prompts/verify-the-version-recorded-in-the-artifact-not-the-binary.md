# Verify the version recorded in the artifact, not the version the binary reports

**Last verified:** 2026-11-13 (12:00 EST) — SkillSpector 2.13.1 on `PATH` vs
2.13.2 in `.ssvenv`; both pins now 2.13.4 and the test reads the constant from
the script.

## The rule

> **When a tool's output is version-bound, compare the version recorded *inside
> the output*, not the version the binary reports.** `--version` answers "what is
> on PATH"; the artifact answers "what ran".

SkillSpector's baseline is version-bound, and the guard compared
`scanner --version`. Two installs, one PATH: whichever answered `--version`
decided whether the baseline was valid. The report itself stamps
`metadata.skillspector_version` — that is the version that did the work.

```python
ran = json.load(open(report))['metadata']['skillspector_version']
assert ran == PINNED_SCANNER
```

## A pin that lives in two files is not a pin

`PINNED_SCANNER` in `scripts/scan_skills.py` and the
`git+https://...@v2.13.2` ref in `ci.yml` had to be kept in sync by memory.
Have the test read the constant from the script instead of hard-coding it.

## The `/tmp` noexec trap, again

`/tmp` is mounted **noexec** here, so pytest's default `tmp_path` breaks any
test that `chmod +x`'s a fake binary: 7 of 9 tests errored with "not an
executable file" and looked like real regressions. Run with
`--basetemp=<repo>/.pytest-tmp`. The mount options are the bug, not the code —
same class as the `/tmp` ENOSPC entry.

## Checklist

1. Version read from the artifact, not `--version`.
2. One source of truth for the pin; the test imports it.
3. `--basetemp` on an exec-capable path for any test with a fake executable.
