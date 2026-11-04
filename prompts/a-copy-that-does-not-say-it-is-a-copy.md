# A Copy That Does Not Say It Is A Copy

**A rule for any repository, package, or published index that contains two
projects with the same code.**

> Found 2026-11-04. `tiny-safeexec` shipped as a **byte-identical clone** of
> `tiny-sandbox`: the same 681-line `tiny_sandbox.py`, the same
> `tests/test_tiny_sandbox.py`, the same `LICENSE` and `SECURITY.md`, and
> a README whose H1 was `# tiny-sandbox`. **The only difference between the
> two repositories was the CI badge URL.** Both declared
> `name = "tiny-sandbox"` in `pyproject.toml`.
> **Last verified:** 2026-11-04 — both modules fetched from the published
> `main` branches and hashed: `md5 = 69f7ea01f3cf10d3038d4e868ba631c2`
> for both files, 23,321 bytes each. The duplicate is now declared in the
> README ("a copy of tiny-sandbox") and excluded from the ecosystem index.

## The Rule

> **Two repos with byte-identical primary modules are one project. Shipping
> both without saying so is a silent trap.**

The reader sees two names, assumes two libraries, and picks one. Whichever
one they pick, the other one exists for no reason they can see.

## The Procedure

1. **Hash the primary module of every repo and compare.** Not the file
   list — the content.

   ```bash
   for r in tiny-*/; do
     printf '%s ' "$r"
     git -C "$r" show HEAD:$(ls "$r" | grep -E '^tiny_[a-z_]+\.py$' | head -1) 2>/dev/null | md5sum
   done | sort -k2
   ```

   Exactly one such pair across 79 repos. One pair is a coincidence; a
   fleet-wide check makes it a measurement.

2. **Check the package name in `pyproject.toml`, not just the repo name.**
   A repo called `tiny-safeexec` that declares `name = "tiny-sandbox"` is
   a **conflict**, not a coincidence. Across 88 repos with a
   `pyproject.toml` there were exactly two duplicate names:
   - `tiny-agent-memory` / `tiny-agent-memory-v2` — **legitimate**. v2 is
     the successor of v1 (`2.0.0` vs `0.1.0`, different code).
   - `tiny-safeexec` / `tiny-sandbox` — **not legitimate**. A copy
     claiming the original's package name.

3. **Check whether the PyPI name is free.** Use the JSON API, not the HTML
   page:

   ```bash
   curl -s https://pypi.org/pypi/<name>/json | python3 -c "
   import json,sys; i=json.load(sys.stdin)['info']
   print(i['name'], i['version'], i.get('author'))"
   ```

   A **200 means the name is TAKEN** (by somebody else, in this case).
   A **404 means it is free**. Never assume a name you use on GitHub is
   free on PyPI.

4. **Either delete the copy, or make it declare itself.** If the copy stays
   for a real reason, its README's first line must say so:

   ```markdown
   # tiny-safeexec (a copy of tiny-sandbox)
   > **This repository is a copy of [`tiny-sandbox`](https://github.com/...).
   >** The library code is byte-identical and the test suite is the same file.
   ```

5. **Exclude it from any published index — with the reason written down.**
   A silent exclusion looks like an oversight; a stated exclusion is a
   decision.

## Why This Is Worse Than A Broken Build

A broken package fails loudly on install. A duplicate:

- passes every test in both repos,
- shows a green badge on both,
- answers to a name that belongs to the other one,
- and appears in a search result as if it were an independent project.

**There is no error anywhere.** The only symptom is a reader who installs
the wrong one and cannot tell why.

See also `prompts/a-readme-on-github-is-not-a-distribution-channel.md` (a
README is not a distribution channel) and
`prompts/pypi-n…cess.md` (a name collision is a silent success).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
