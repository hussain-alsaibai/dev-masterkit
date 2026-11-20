# A Drift Test Can Measure The Long Part And Miss The Line

**Last verified:** 2026-11-20

## The prompt

> You have a test that guards a generated or hand-maintained doc file. Read it
> and answer two questions, in this order:
>
> 1. **Which line in that file does a reader ACT on?** Name it — usually the
>    install command, the import path, or the CLI binary name.
> 2. **Does the test assert on that line?** Not on the file, not on its
>    header — that line.
>
> If the answer to (2) is no, the test is a **coverage-shaped object**: it is
> large, it is green, and it guards the parts of the file where being wrong is
> cosmetic. The part where being wrong is fatal is unguarded.
>
> Then, before you write the guard:
>
> - **Prove it red on the ORIGINAL file.** `git show HEAD:<file>` piped into the
>   checker. A guard that has only ever seen the fixed file has not been tested.
> - **Prove it green on the FIX**, and confirm the one file that was already
>   correct still passes. A guard that passes everything is not a guard; a guard
>   that fails the correct file will be deleted by the next person.

## Why this exists

`tiny-config` and `tiny-validator` both shipped a `test_llms_drift.py`. Both
passed, every day, for months. Both repos' `llms.txt` told an AI agent to run
`pip install <own-name>` — and that name was not on PyPI.

Read the test on `origin/main` and the shape is immediate: seven tests, and
they assert the version header, the Python floor, the exported API list, and a
masking table. **Thousands of words of coverage, and not one assertion on the
line the reader executes.** The install command was the entire point of the
file, and it was the only unmeasured line in it.

Coverage that is *large* is not coverage that is *placed*.

## The trap in writing the guard

Three drafts were written for this. Two were wrong in ways only running them
revealed:

1. **"The package name is in `pyproject.toml`"** — passed on all three broken
   files. Of course it did: the declaration is the claim under suspicion. A
   repo can write `name = "tiny-config"` while PyPI hands that name to someone
   else entirely.
2. **A six-line forward window for the warning note** — reached past `- Docs:`
   and let `tiny-cli` pass by accident, for the wrong reason. It was correct
   output from an incorrect rule.
3. **Moving the warning above the install line** — then the *corrected* files
   failed their own test, because the note landed inside the window.

Every one of those bugs was invisible when reading the diff and immediate when
run against `git show HEAD:llms.txt`.

## The check that settles it

```
pip download <name> --no-deps          # before: "No matching distribution found"
pip download "<name> @ git+https://github.com/<org>/<repo>.git"
                                       # after: "Successfully downloaded"
```

A curl of `https://pypi.org/pypi/<name>/json` returning **404** is the same
fact one step earlier and costs one request. That is how the unclaimed names
were separated from the squatted ones.
