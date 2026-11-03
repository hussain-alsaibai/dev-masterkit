# A Partial Failure Is Not A Pass

**A rule for any monitor, watcher, poller, or sweep that reports a single
status for a list of subjects.**

> Found 2026-11-03. The PR monitor printed `NO_CHANGES` and exited **0** while
> **3 of 9** PR checks had failed with `GitHub API 503 ... Service Unavailable`.
> **Last verified:** 2026-11-03 — the exit-code logic was read directly out of
> `skills/pr-monitor/pr-monitor.js` (lines 300-309) and confirmed by inspection.

## The Rule

> **A green exit code means "every subject was checked and none changed".
> If any subject was not checked, the result is UNKNOWN, not a pass.**

## The Defect, In Source

```js
if (failures.length) {
  console.error(`[pr-monitor] ${failures.length}/${list.length} PR checks failed`);
  // ... only when EVERY one failed:
  if (failures.length === list.length) {
    console.error('CHECK_FAILED');
    process.exit(2);
  }
}
console.log('NO_CHANGES');   // <-- printed even with 3 of 9 unchecked
```

`failures.length === list.length` is the only condition that produces a
non-zero exit. **3 failures out of 9 falls through to `NO_CHANGES` and exit 0.**

The failure message itself went to **stderr**; the pass message went to
**stdout**. A scheduler that reads only stdout saw a clean success.

## Why This Is The Worst Monitor Failure Shape

| shape | what the operator sees |
|---|---|
| monitor crashes | loud — the job is red |
| monitor reports nothing | loud — the job is red |
| **monitor reports a pass it did not earn** | **silent — the job is green** |

A partial failure is a *coverage* failure wearing a *result* failure's
clothes. The report is not wrong about what it found; it is **silent about
what it did not look at**.

## The Procedure

1. **Count what was checked, not what was found.** The denominator is the
   watch list size, and it must be asserted.
2. **Separate "no change" from "not checked".** They need different
   vocabulary: `NO_CHANGES` and `PARTIAL_CHECK_FAILED` are different claims.
3. **Never let a non-zero count of failures coexist with a zero exit code.**
   The exit code must reflect the *worst* outcome, not the modal one.
4. **Read stderr as well as stdout.** The diagnostic was on stderr; the verdict
   was on stdout. A log aggregator that keeps only one of them keeps the
   wrong one.

## The Fix Shape

```js
const checked = list.length - failures.length;
if (failures.length) {
  console.error(`[pr-monitor] ${failures.length}/${list.length} PR checks failed`);
  // Any failure at all is a non-zero exit. Partial is not a pass.
  console.error(failures.length === list.length ? 'CHECK_FAILED' : 'PARTIAL_CHECK_FAILED');
  process.exit(2);
}
if (checked !== list.length) {
  console.error('PARTIAL_CHECK_FAILED: not every subject was checked');
  process.exit(2);
}
console.log('NO_CHANGES');
```

## The Retry Is Free — So Retry Before You Act

A failed check **does not update that PR's stored state**, so nothing is lost
by running the check again. The retry costs one API round and is safe:

- Retry reports **9/9, no failures** -> the earlier `NO_CHANGES` was genuine,
  and the earlier failure was transient.
- Retry fails again -> a real failure to report, not a silence to send.

**A partial failure is never an excuse to report nothing.**

## The Generalisation

Anywhere a loop reports one verdict for many items: CI matrices, link
checkers, health sweeps across repos, migration verifiers, audit scanners.
The failure mode is identical - a denominator that shrinks silently.

See also `prompts/zero-tests-ran-is-a-failure.md` (a suite that collects zero
tests and reports green) and
`prompts/a-stale-error-counter-is-not-a-live-failure.md` (a counter that
describes the past rather than now).
