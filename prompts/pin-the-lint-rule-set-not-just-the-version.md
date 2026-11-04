# Pin The Lint Rule Set, Not Just The Version

**A rule for every project whose CI runs a linter.**

> Found 2026-11-04. `tiny-worktree` passed lint **locally** on ruff 0.15
> and failed in CI on ruff 0.17 with **62 findings**, almost all `UP031`
> (percent-format). The code was fine. **The rules changed underneath it.**
> **Last verified:** 2026-11-04 — reproduced by running ruff 0.17 against
> the pre-fix tree; the fixes that shipped address every finding, with
> `UP031` and `UP032` ignored **on purpose** because the package supports
> Python 3.8 and percent-format is the most portable spelling.

## The Rule

> **A linter's version is not its behaviour. Pin the rule set explicitly, or
> a routine dependency bump turns your build red for reasons nobody chose.**

`ruff` (like `pylint`, `eslint` and `rubocop`) ships **new default
rules** in minor versions. If you did not write a `select` list, you
opted into every rule they enable, including the ones that did not exist
when you last ran it.

## The Failure Shape

```
locally:  ruff 0.15  -> clean
CI:      ruff 0.17  -> 62 findings
```

Nothing in the code changed. The badge went red on a dependency bump, and
the natural — wrong — response is to mass-rewrite working code into
whatever shape the new rule prefers. Some of those rewrites are **worse**
for the versions you claim to support.

## The Procedure

1. **Write the rule set into the project**, not just the version:

   ```toml
   [tool.ruff]
   target-version = "py38"
   line-length = 100

   [tool.ruff.lint]
   select = ["E", "F", "W", "I", "B", "UP"]
   ignore = ["UP031", "UP032"]
   ```

2. **Ignore deliberately, with a reason.** `UP031` is ignored on purpose
   when the package supports Python 3.8 — percent-format is the most
   portable spelling.

3. **Pin the linter version in CI**, so a green run means "green under the
   rules we chose":

   ```yaml
   - name: Install linter
     run: pip install "ruff==0.17.0"
   ```

4. **Run the SAME version locally that CI runs.** A local pass proves
   nothing when the versions differ.

   ```bash
   pip install "ruff==0.17.0" && ruff check .
   ```

5. **Fix what is real, suppress what is a deliberate choice.** The 62
   findings were not all noise: the non-`UP031` ones were fixed properly
   rather than suppressed. **A blanket `ignore = ["ALL"]` is a fix that
   deletes the linter.**

## The Generalisation

The same rule applies to every tool whose output is a contract:

- `eslint` with `--max-warnings 0` and a changing default rule set,
- `mypy` with `strict = true` and a new check in a minor release,
- `actionlint`, `shellcheck`, `gopls`,
- `black` and `ruff format` — a formatting change is a **diff storm** in
  a repository with a sensitive history.

**Pin the configuration, or pin the version, or do both. Never leave the
behaviour to the upstream default.**

See also `prompts/python-support-is-a-claim.md` (a version floor is a
claim you have to execute) and `prompts/validate-workflow-schema.md`
(a tool that reports on your repo needs a pinned vocabulary too).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
