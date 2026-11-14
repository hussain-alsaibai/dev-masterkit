---
name: a-security-commit-that-does-not-grep-the-tree-is-not-a-fix.md
description: Use when a credential, key, or token may be committed — a prior "remove leaked keys" commit removed a different set of files, and the secret survived both.
---

# A security commit that does not grep the tree is not a fix

## The prompt

> You are told a leaked secret has been handled. Verify it against HEAD, not
> against the commit message:
>
> 1. Read the **exact literal**, then `git grep -n <literal> HEAD` across the
>    whole tree. A remediation commit that fixed five files is not evidence
>    about the sixth.
> 2. Check the **history**, not just HEAD: `git log -S<literal> --oneline`.
>    A file deleted from the working tree is still published in history.
> 3. Enumerate every surface: workflow files, docs, press copy, `.txt` content,
>    audio/video scripts. Grep the literal, not the filename pattern.
> 4. Before calling the exposure a catastrophe, prove the **blast radius
>    on-chain / on-network**: does the key control anything privileged?
>
> A rewrite un-publishes nothing already fetched. The secret stays
> compromised after the fix; say so.

## Why

`hussain-alsaibai/claw-token` is a **public** repo. A testnet private key was
committed in the initial commit `7b6ee32` and was still present at HEAD in
four files: `wallet.json`, `THIRWEB_DEPLOY_GUIDE.md`, `deploy_now.py`,
`deploy_python.py`.

Two prior security commits existed:

- `c688a6d` "Remove leaked private keys"
- `ea910aa` "Add .gitignore to prevent future leaks"

They removed a **different** set — `.env`, `deploy-tenderly.js`,
`live-deploy.js`, `tenderly-deploy.js`. The key survived both, for ~8 months.
A remediation written against a file list is not a remediation.

## Blast radius is a measurement, not a guess

The instinct on an exposed deploy key is "everything is owned". Here the
measurement said otherwise:

- `owner()` on the live contract returns the **CI deployer** address, not the
  exposed key's address.
- Every privileged function in the contract is `onlyOwner`.
- So the exposed key could not call `setTax`, `setRewardPool`,
  `setMaxWalletAmount`.

Still real: the key was public for eight months and its wallet held 1 ETH of
virtual-testnet funds. An honest report says both halves.

### The network mistake that would have ended the investigation early

The contracts are deployed on a **Tenderly Virtual TestNet** that merely shares
chain ID 84532 with Base Sepolia. Querying `https://sepolia.base.org` returns
**0 code bytes** for every address — which reads as "never deployed".

The RPC to use is the repo variable: `gh api repos/O/N/actions/variables`.
A "not deployed" conclusion from a public RPC is a conclusion about the wrong
chain.

## The removal, in two commits

1. Literal removed from all four files; `wallet.json` keeps the address with a
   placeholder; deploy scripts read `PRIVATE_KEY` from the environment with
   **no literal fallback**; the file and `broadcast/` untracked and ignored.
2. History rewritten. `git-filter-repo` was not installed, so the orphan-branch
   pattern was used: a new root commit carrying the full tree, force-pushed.

The dry run is what made the force push safe:

```
git diff --name-status origin/main HEAD | grep -c '^D'   -> 0
tree sha on both sides                                   -> identical
```

The published tree did not change at all — only the history. The old history
is kept locally under a tag and never pushed.

## Two greps that lie

- **`0x[0-9a-f]{40}` matches transaction hashes.** A 64-hex tx hash's first 40
  characters match the address pattern. Check total length before treating a
  string as an address — one "address" in that README was a transaction hash.
- **One file is not the surface.** After the key fix, a second sweep found 27
  places claiming the wrong network and 19 address occurrences across 29 files:
  whitepaper, press kit, press release, DEX listing forms, AMA script, tweet
  thread, 8 daily content files, meme batches. The press copy is where a wrong
  address does the most damage and the easiest to forget, because it is not
  markdown.

See also `prompts/credential-order-is-not-validity.md` (two credentials under
one name, and the env var shadows the working one) and
`skills/credential-recovery/`.

Last verified: 2026-11-14 — literal absence re-checked with `git grep` and
`git log -S` against the published remote; `owner()` read from the live
Tenderly vnet via the repo's `TENDERLY_RPC_URL` variable.
