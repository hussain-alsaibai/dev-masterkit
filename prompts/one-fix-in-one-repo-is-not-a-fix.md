# One Fix In One Repo Is Not A Fix

**A rule for every defect you have already fixed once, in a fleet where the
same code is shipped more than once.**

> Found 2026-11-04. `tiny-agent-eval` shipped the **same evaluator** as
> `tiny-eval`, and carried the **same bug** that had already been fixed in
> `tiny-eval` v1: `Evaluator.run()` saved the result but never called
> `_append_index()`. The index is what `list_results()` and
> `regression_check()` read, so both were permanently broken:
>
> ```
> list_results()      -> []  (always)
> regression_check()  -> {'trend': 'unknown'}  (always)
> ```
>
> **Last verified:** 2026-11-04 — the duplicate was found by a CI sweep, not
> by remembering the earlier fix. Both repos now pass a fresh-clone check:
> `tiny-agent-eval`'s `list_results()` returns 2 and its trend is
> `regressing`.

## The Rule

> **After fixing a defect, search for every repo that ships the same code and
> re-check it. The second copy is still broken, and nobody is looking at it.**

A fix propagates to the repo you fixed in. It does not propagate to the
clone, the fork, the vendored copy, or the "v2" that was cut from the same
source six months ago.

## The Procedure

1. **Identify the fixed code by its content, not by its name.** A duplicate
   does not carry the original's filename.

   ```bash
   # hash the primary module of every repo in the fleet, then group
   for r in */; do
     f=$(ls "$r" | grep -E '\.(py|js|ts)$' | grep -v test | head -1)
     [ -n "$f" ] && printf '%s %s\n' "$(md5sum < "$r/$f" | cut -d" " -f1)" "$r"
   done | sort | awk '{print $1}' | uniq -d
   ```

2. **For near-duplicates, diff them.** A byte-identical hash catches a copy.
   A copy with one changed line needs a diff:

   ```bash
   diff -u repoA/tiny_eval.py repoB/tiny_eval.py
   ```

3. **Check the fix landed in each copy, not just in the original.** The bug
   is a *pattern*, and the pattern may have been re-implemented rather than
   copied.

4. **Re-run the same test against every copy.** A test that passes in the
   original and fails in the sibling is proof, and it is the cheapest proof
   there is.

## The Near Misses In The Same Sweep

Three more findings from the same pass, all in published code:

- **A test file that cannot even be collected.** `tiny-agent-eval`'s root
  `test_tiny_eval.py` imported seven names the library never had
  (`eval_expr`, `Sandbox`, `interpolate`, ...). It failed collection on
  every Python version. **A test file that cannot be collected is worse than
  no test file** — it makes `pytest` at the root look broken.
- **A test fixture that cannot produce the behaviour it asserts.** The
  criterion was `lambda ctx: True`, so the context was ignored and no
  score drop could ever occur. The test asserted a behaviour its own
  fixture made impossible.
- **A missing pytest read as a pass.** `python3.10 -m pytest` on a host
  without pytest printed `No module named pytest`, and the classifier
  treated it as success because the string contained neither `failed` nor
  `error`. **Classify on the exit code, never on a substring of the
  output.**

## The Generalisation

The same rule applies to:

- a `fixup` commit applied to one copy of a vendored file,
- a security patch applied to one fork,
- a version bump applied to one release branch,
- a config change applied to one environment.

**Each of those is a fleet-wide operation wearing the costume of a local
one.**

See also `prompts/capture-before-you-reset.md` (a stash is not
automatically unpublished work) and
`prompts/a-copy-that-does-not-say-it-is-a-copy.md` (the byte-identical
version of this problem).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
