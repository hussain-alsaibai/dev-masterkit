---
name: self-auditing-repo
description: "Audit a library repo against its own claims and its own published artifact - run the suite from an unpacked sdist, prove tamper/security detection by attacking it, prove a test file is actually collected, and prove each fix by making the new test fail against the old version. Use before calling a repo done, when a green badge sits on top of a suspicion, or when asked whether a package genuinely does what its README says."
---

# self-auditing-repo — make the repo prove its own claims

**Last verified:** 2026-11-11

A green CI badge answers exactly one question: did the commands the workflow
runs exit 0. It does not answer "does the published artifact work", "does the
security property hold under attack", "did this file get collected", or "does
this new test fail on the old code". This is the procedure that answers those
four, in the order that finds the most defects per minute.

Derived from four defects found in one day (snapdb 0.18.1, tiny-cli 1.3.1,
tiny-log, tiny-audit 0.2.0) — each in a repo that looked healthy.

## When to use

- Before declaring a library repo "done"
- After any change to packaging (`MANIFEST.in`, `pyproject`, entry points)
- After any change to a security-relevant check (`verify`, `auth`, redaction)
- When the suite total has not moved after adding tests

## Step 1 — run the suite from the artifact, not the checkout

```bash
uv build --sdist && tar xzf dist/*.tar.gz && cd */ && pytest -q
```

The checkout is the one tree where a packaging defect cannot appear. Compare
the count with the checkout's count.

- **Missing file → `FileNotFoundError`**: the test reads something
  `MANIFEST.in` does not ship.
- **`fixture 'name' not found` on every run**: a module-level helper named
  `def test(...)`. pytest collects it. Rename to `check()`.

Fix `MANIFEST.in`, then add a guard test asserting the tarball contains every
file the suite reads, that `PKG-INFO`'s version matches `__version__`, and that
no module defines a collectable `test()` helper (an AST walk is five lines).

See `prompts/a-test-that-only-runs-in-a-checkout-is-a-test-that-never-ran.md`.

## Step 2 — count what CI actually collected

```bash
pytest --collect-only -q | tail -1     # total
find tests -name 'test_*.py' | wc -l   # files
```

If a file contributes zero, CI either names files individually or a matrix
runs one file per command. Replace the file list with `pytest .`.

**A per-file matrix also hides cross-file state.** Module-level latches
(`_NO_COLOR = resolve()` from `isatty()` + env) behave differently when one
process imports many test modules. Set such env vars in `conftest.py`, never in
a test module body.

See `prompts/ci-that-is-not-auto-triggered-is-ci-that-ran-once.md`.

## Step 3 — attack the security property

Take the thing the library claims and do the cheapest hostile thing to it:

| library | claim | attack | what 0.1.0 did |
|---|---|---|---|
| `tiny-audit` | `verify()` detects tampering | truncate the log to 1 of 3 entries | `True` |
| redaction | cannot leak | block the import at module load | (see the sealed-import prompt) |
| an audit chain | order matters | delete a middle entry | detect **only** if `seq` is in the HMAC |

Then fix, and **watch the side table**, because the obvious fix has a mode
where it disables itself:

- A high-water mark written unconditionally by the constructor is rewritten
  from the truncated log, so `verify()` compares the log to itself. Write it
  **raise-only**.
- A witness the writer can repair is not a witness. State the remaining limit
  and pin it with a test.

See `prompts/a-witness-the-writer-can-repair-is-not-a-witness.md`.

## Step 4 — prove every new test fails on the old version

```bash
git stash && pytest tests/ -q     # or: pip install <old version>
git stash pop
```

All of them must fail. A security fix whose tests pass on the vulnerable
version tests the harness, not the fix. The same applies to mutation testing:
write a script that removes ONE behaviour at a time and asserts the suite goes
red — six mutations should produce six separate failures, not one.

## Step 5 — check the build config cannot reach production unheard

If the repo deploys (a contract, a package, a service), read the deploy script
**before** pushing:

- constructor arity matches the new contract,
- the release trigger is `workflow_dispatch`, not `push`,
- a side-effecting job with a secret never shares a trigger with ordinary
  commits.

See `prompts/a-ci-job-with-a-credential-and-a-side-effect-must-not-share-a-trigger.md`.

## Output

Report the four numbers and what each was measured from:

```
artifact suite   unpacked sdist      236 passed / 5 skipped   (checkout: 238)
collected        pytest --collect    243 (+5 previously uncollected)
mount            findmnt -T /tmp     noexec -> --basetemp on the overlay
tamper attack    3 -> 1 entries      detect: False -> True
new tests vs old 9/9 fail on 0.1.0
```

A count with no stated source is the defect the next session inherits.
