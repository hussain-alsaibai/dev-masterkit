# A Mock Proves The Mock Works

**A rule for every test suite that stubs out the thing the library wraps.**

> Found 2026-11-04. Two new repositories were written to test against the
> **real** tools — real throwaway git repositories, real JSON schemas — and
> both suites caught a genuine defect that no amount of reading would have:
>
> - **`tiny-worktree`** — `git worktree add` was called with the arguments
>   in the wrong order (the **path must precede the commit-ish**), and
>   `prune(dry_run=True)` was **not actually a dry run**.
> - **`tiny-mcp-contract`** — a **removed** tool was classified `GONE` but
>   did not count as breaking, so the CI gate would have **PASSED** on the
>   exact change that breaks every caller of that tool.
>
> **Last verified:** 2026-11-04 — both suites pass against the real tools
> (`tiny-worktree`: 37 passed, 1 skipped; `tiny-mcp-contract`: 54 passed).
> Both defects were reproduced against the real `git` binary and the real
> schema before the fix.

## The Rule

> **When the package is a wrapper around a real tool, test against that
> tool. A mock proves the mock works.**

The bugs above are **argument-order bugs** and **flag-semantics bugs** —
exactly the class a mock hides. A mocked `git` accepts any argument order.
A mocked schema validator accepts any schema. **The mock was more
permissive than the thing it stood in for, and the code was written to
match the mock.**

## The Procedure

1. **Use the real tool, in a throwaway directory.** A real git repository
   costs one `git init`. A real JSON Schema costs one `jsonschema.validate`.

   ```python
   def make_repo(tmp_path):
       subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
       subprocess.run(["git", "-C", str(tmp_path), "config",
                       "user.email", "t@example.com"], check=True)
       subprocess.run(["git", "-C", str(tmp_path), "config",
                       "user.name", "T"], check=True)
       return tmp_path
   ```

2. **Do not mock the boundary you are wrapping.** Mock the network when you
   wrap an HTTP client; do not mock the git binary when you wrap git.

3. **Assert the *state* after a dry run, not the log line.**

   ```python
   before = wt.list_worktrees()
   wt.prune(dry_run=True)
   assert wt.list_worktrees() == before   # nothing changed
   ```

   `--verbose` is not a dry run. `-n` is. **Only the state tells you which
   one you got.**

4. **Assert the exit code of a gate, not its output.**

   ```python
   rc = cli(["gate", "--base", "old.json", "--head", "new.json"])
   assert rc == 1   # a breaking change must fail the build
   ```

   A gate that always returns zero is worse than no gate, because it
   teaches people to ignore it.

5. **Test the failure the tool actually produces.** If `git worktree add`
   rejects an argument order, the test must use the order git rejects.

## The Generalisation

The same rule applies to:

- a library that wraps `docker` — test against `docker`,
- a library that wraps `sqlite3` — test against a real database file,
- a library that wraps an HTTP API — test against a real local server, not
  a hand-written JSON blob.

**Every mocked boundary is an untested assumption about the real one's
strictness.**

See also `prompts/ci-target-must-match-repo-layout.md`,
`prompts/mutation-test-proves-the-test.md` (a test that cannot fail proves
nothing) and `prompts/zero-tests-ran-is-a-failure.md`.

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
