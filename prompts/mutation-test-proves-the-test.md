# Mutation Testing — Prove the Test Can Fail

**A test that has never failed is not evidence.**

> Found 2026-10-25 while writing `url_redaction.redact_urls_in_text` tests
> for `pipeshub-ai/pipeshub-ai#4650`. Nine new tests, 185 passing in the
> file. That number proved nothing on its own, so five mutants were injected
> into the implementation. **All five were killed.** **Last verified:**
> 2026-10-25.

## The Argument

A passing test is consistent with two worlds:

1. The code is correct and the test checks it.
2. The code is broken and the test does not check it.

Only one of those worlds is what you meant. **Green says nothing on its own
about which one you are in.** A test that asserts nothing, asserts the
wrong thing, or asserts a constant will pass forever, in both worlds,
identically.

So the question is not "does the test pass?" It is:

> **Does the test fail when the behaviour is broken?**

## The Method

Take the implementation and deliberately break it, one way at a time, then
check that the test suite notices. Each injected defect is a **mutant**.

For `redact_urls_in_text`, five mutants were injected and all five were
caught:

| # | Mutant | What it broke | Killed? |
|---|--------|---------------|---------|
| 1 | Matcher consumes the whole sentence | `Visit https://x.com now` → whole string replaced | yes |
| 2 | Query string kept | `https://x.com?a=1` → query survives | yes |
| 3 | Trailing period stripped | `https://x.com.` → period removed | yes |
| 4 | Userinfo kept | `https://u:p@x.com` → credentials survive | yes |
| 5 | Only the first URL redacted | two URLs → second one untouched | yes |

**5 injected, 5 killed.** A mutant that survives is a gap in the suite, and
the gap is exactly as important as a failing test — more so, because a
failing test announces itself and a gap does not.

## The Procedure

1. **Enumerate the behaviours** the spec pins. One mutant per behaviour.
   The mutants are the spec turned into sabotage.
2. **Inject one mutant at a time.** Combined mutants hide each other: two
   bugs that cancel out produce a green suite.
3. **Run the suite.** A surviving mutant is a missing assertion.
4. **Write the missing assertion**, then re-run with the mutant still
   injected. It must now fail.
5. **Remove the mutant.** The suite must go green again.
6. **Repeat** until every behaviour in the spec has a mutant that dies.

Step 4 is the one that is skipped, and it is the one that matters: writing
the assertion *while the mutant is live* is what makes the assertion
specific. Written afterwards, against green code, it is a guess.

## The Cost Question

Mutation testing is more expensive than writing tests. That is true, and
it is still worth it, because the cost is bounded and the alternative is
unbounded:

- Mutants are cheap: a one-line edit, run, revert.
- A test that cannot fail is paid for on **every future change** — it is
  a permanent false guarantee that gets re-earned every time the code
  moves.

For a contribution task where a reviewer will ask "what does this test
actually check?", a mutation run is the answer. For your own codebase, do
it on the behaviour you most doubt.

## The Sibling Discipline

The same idea, applied to the test suite rather than to individual
assertions, is the regression-test rule:

> **A regression test must fail against the original code.** Revert the fix
> in a scratch copy and confirm the new test fails there. A test that passes
> both before and after the fix proves nothing.

That rule was verified on 2026-10-25 in the same session: the
`context-bridge` test suite was confirmed to FAIL against the original code
and PASS against the fix, by reverting a copy and running it.

## The Generalisation

> **A green suite is a statement about the code, not about the tests.**
> To learn something about the tests, you have to watch them fail.

This is the same argument as
`prompts/zero-tests-ran-is-a-failure.md` (a suite that collects zero tests
reports green) and
`prompts/spec-literal-must-be-generated.md` (a test can pass against a
literal that was never in the spec). Three different ways for green to
mean nothing. Check each one:

1. Did the suite actually collect and run the tests?
2. Did the test assert against the real spec?
3. Can the test fail when the behaviour is broken?

See also `prompts/readme-claims-must-be-runnable.md`.
