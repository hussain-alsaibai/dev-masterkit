# Audit the public artifact, not just the docs

**Discovered:** 2026-11-15 (CLAW marketing site `index.html` vs the contract)
**Last verified:** 2026-11-15 — deployed URL re-fetched after the pages
workflow went green: `Tax: 3% total (2% Burn, 1% Reward Pool)` present,
`Tax: 5%` count **0**, `burned forever` and `Initial Burn` both **0 hits**.

## The claim

The README was audited because a reminder pointed at it, and its numbers were
corrected to match the chain. Sitting in the same repo, served from
`index.html`, was a **live public page** making a completely different set of
claims. Every number contradicted the contract:

| Claim on the site | On-chain truth |
|---|---|
| "1% burned forever on every transaction" | `burnBps` = 200 = **2%** |
| "2% redistributed to holders" | `rewardBps` = 100 = **1%**, and the pool is the **dead wallet** |
| "Tax: 5% (2% Holders, 2% Marketing, 1% Burn)" | `totalTaxBps` = 300 = **3%**. No marketing tax exists. |
| "Liquidity Pool (Locked)" — 50% (500M) | No pool. The contract minted all 1B to the deployer. |
| "Initial Burn — 5% (50M)" | **0** burned; `balanceOf(dead)` reverts. |
| "AI provides daily market insights" | No such feature exists in the repo. |

## The rules

> **A marketing site is the most-read document in a repository and the least
> audited one.** Fixing the README and stopping leaves the wrong numbers on
> the page users actually visit.

> **"Redistributed to holders" is a claim about a mechanism, not a number.**
> The 1% pool pointed at `0x…dEaD` because no staking contract existed — the
> tokens were *destroyed*, not distributed. The percentage was right and the
> outcome was wrong.

> **A tokenomics pie chart is a statement about where tokens ARE, not where
> they are supposed to go.** The contract minted 1,000,000,000 to the
> deployer. Every row of the allocation table was aspirational.

## The check

```bash
# 1. every number in the site against the contract
curl -s https://<site>/ | grep -oE '[0-9]+%'
# 2. every one of those strings against the chain: burnBps, rewardBps,
#    totalTaxBps, totalSupply, balanceOf(0x…dEaD)
# 3. re-fetch the DEPLOYED url after the deploy goes green
grep -c 'Tax: 5%' /tmp/page.html    # must be 0, not "the PR fixed it"
```

Step 3 is the one that gets skipped. A merged PR is not a deployed page; the
count on the deployed URL is the only evidence that readers see the fix.

## Why it recurs

Docs get audited when something points at them. Nothing points at
`index.html` — it is a sibling file that ships to production. Enumerate the
repo for every artifact a user can reach (README, site, `docs/`, package
long-description, social bios) and check each against the same source.
