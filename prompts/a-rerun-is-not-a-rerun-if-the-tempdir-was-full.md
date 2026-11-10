# A rerun is not a rerun if the tempdir was full

**Last verified:** 2026-11-10

## The situation

A 1,000+ test suite reported `81 failed, 970 passed` with an
`INTERNALERROR` above it:

```
OSError: [Errno 28] No space left on device
```

The host's `/tmp` is a **512 MB tmpfs**, and pytest's `tmpdir` lives there by
default. The failures looked like a code problem — 81 tests, spread across
several modules, in the repository being rebased.

Re-running the same suite with the base directory moved to the overlay
filesystem, and **no code change at all**:

```bash
pytest hub/agents/email/python/tests/ --basetemp=/home/node/pt
```

```
2376 passed, 3 skipped
```

**The same commit. The same interpreter. 81 failures became 0.**

## Why it is not just "check disk space"

The dangerous property is that **a full disk is invisible in the summary
line**. `81 failed` reads exactly like `81 failed` from a real regression. The
only signal that separates them is the `INTERNALERROR` line a few rows above,
and it scrolls off first.

Worse: pytest's own error handling for `ENOSPC` during `tmpdir` creation can
surface as a *test-local* exception — `FileNotFoundError` on the file a fixture
was supposed to write into the temp dir — so the traceback points at the
fixture, not at the disk.

## Why it happens here specifically

Per AGENTS.md (2026-10-29): `/tmp` on this host is a 512 MB tmpfs, and it
fills from tool output spill files (web-fetch logs), stale virtualenvs, and
large clones. pytest adds one directory per test, plus one per run of
`--basetemp`, plus cloned-repository copies.

A rebase makes it worse: you typically have three checkouts open at once
(`/tmp/<repo>`, the worktree for the base, and the rebuild target).

## The procedure

1. **`df -h /tmp` is the first command, before reading any failure.** One
   second, and it rules the whole class in or out.
2. **Grep the output for `INTERNALERROR` and `Errno 28`** — not just the tail.
   `pytest -q 2>&1 | grep -E 'INTERNALERROR|Errno 28'`.
3. **Re-run with `--basetemp` on the overlay**, using a directory with real
   space (`df -h` it, not `/tmp`).
4. **Only then** treat remaining failures as real. Compare against the base
   branch in a separate `git worktree` so "pre-existing" is a measurement.
5. **Sweep before a long run**: remove temp dirs nothing holds open. Check
   `/proc/*/cwd` and `/proc/*/fd` for each candidate before deleting, and skip
   anything touched in the last 20 minutes — a live `pytest` run looks exactly
   like a stale directory.

## The generalisable rule

> **A resource failure that the harness reports as a test verdict has to be
> ruled out before the verdict is believed.** Disk-full, OOM-killer, fd
> exhaustion and a killed subprocess all wear the shape of a code regression,
> and all of them are falsified by re-running under conditions where the
> resource is adequate.

The corollary that costs the most time: **do not debug the tests until the
environment has passed its own check.** Copying 81 failing test names into an
analysis is 81 opportunities to find a plausible-but-wrong cause.

## Counter-rule

A full disk can also cause a *genuinely* intermittent failure — a test that
writes a large fixture gets a short write and asserts on a truncated file. In
that case the re-run passes and the code is still fine, but the test now sits
on a resource it does not control. Fix the test (write to a managed temp path,
assert on content) rather than enlarging the disk.

## Verified

- Host: `/tmp` = `tmpfs 512M`, overlay 14 GB free at the time.
- `4 tests / 48 tests` in `dev-masterkit` itself re-run in a fresh clone the
  same day: **48 passed** — this prompt's own suite is not affected, which is
  the point: the check is cheap enough to always run.
- Live example: an email-agent suite went 81 failed -> **2376 passed, 3
  skipped** on `--basetemp` alone. See `daily-updates/2026-11-10.md`.
