# A vendored directory is an undeclared build step

**Discovered:** 2026-11-11 (claw-token, `da23096` → `1c00b63`)
**Last verified:** 2026-11-11 — reproduced from a clean tree with
`git archive HEAD | tar -x -C /tmp/x`, then reproduced the fix the same way

## What happened

`claw-token` had **436 `node_modules` files tracked**. `node_modules/` had been
in `.gitignore` since the first commit — and was also committed in that same
commit, because **a `.gitignore` rule does not untrack a file that is already
tracked**. The ignore rule looked like protection while 443MB of dependency
tree shipped in every clone.

The untrack itself was trivially correct. CI went red anyway on the push.

## Why CI went red

`foundry.toml` set `libs = ["node_modules", "lib"]` and remapped
`@openzeppelin/` into `node_modules/`. The Foundry workflow ran `forge build`
with **no install step at all** — because the vendored tree *was* the install.

```
Error (6275): Source "node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol" not found
```

Every import resolved to a directory that no longer existed.

## The rule

> Before untracking a vendored directory, grep the CI workflow and every build
> config for what points into it: `libs`, `remappings`, `include`, `NODE_PATH`,
> `vendor/`, `LIBRARY_PATH`. The vendored copy answering an import is easy to
> mistake for the project not needing an install.

Removing it converts a hidden dependency into a visible failure — the right
outcome, but it has to be paid for in the same change.

| step | before | after `1c00b63` |
|---|---|---|
| `npm ci` | not run | exit 0 |
| `forge fmt --check` | — | clean |
| `forge build --sizes` | Error (6275) | exit 0 |
| `forge test` | — | 21 passed |

## Reproduce from a clean tree before fixing

`git archive HEAD | tar -x -C /tmp/x` gives the exact bytes CI checks out: no
`node_modules`, empty submodule. If it builds there, the problem is
environment, not code. Here it failed with the identical `Error (6275)`, which
is what made the missing install step diagnosable in one pass.

## Check `.gitignore` for the whole family at the same time

Same repo, same root cause: **48 tracked `out/` files** — forge's build output
— while `cache/` and `artifacts/` were already ignored. `out/` was simply
missing from `.gitignore`. Verified regenerable (`rm -rf out cache && forge
build`) before untracking. One audit caught both.

## A move through `/tmp` is a copy through a 512MB tmpfs

`mv node_modules /tmp/…` produced ~250 `ENOSPC` errors. `mv` across
filesystems copies then deletes, so a failure leaves the source intact but the
tree half-processed. Use `git archive`, or a same-filesystem path.
