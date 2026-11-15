# "Empty code" is relative to the chain the deployment was made on

**Discovered:** 2026-11-15 (CLAW contract reported as "NOT deployed")
**Last verified:** 2026-11-15 — measured directly:
vnet RPC `eth_chainId` → `0x14a34` (84532), `mainnet.base.org` → `0x2105`
(8453); `eth_getCode` for `0x6ae6829d…` returns a full contract body on the
vnet and `0x` on Base mainnet.

## The claim

A recurring reminder reported the contract `0xA4316288…` as returning empty
code on Base and therefore **"NOT deployed"**. It was checked against five
public RPCs:

| RPC | chain | `eth_getCode` |
|---|---|---|
| base-rpc.publicnode.com | mainnet | 0 bytes |
| mainnet.base.org | mainnet | 0 bytes |
| base.meowrpc.com | mainnet | 0 bytes |
| base-sepolia-rpc.publicnode.com | sepolia | 0 bytes |
| sepolia.base.org | sepolia | 0 bytes |

Five of five agreed, and every one of them was asking the wrong question. The
contract was deployed to a **Tenderly Virtual TestNet**, whose RPC answered
`0x14a34` — chain ID **84532**, the same number as Base Sepolia, but a
different network entirely.

## The rule

> **`eth_getCode` returning `0x` says "no code on the chain you asked".
> It does not say "no deployment exists".** Report the RPC and the chain ID
> alongside the result, and look up the deployment transaction before
> declaring anything undeployed.

Agreement between RPCs is not corroboration when they are all on the same
network.

## The checks that settle it

```bash
RPC=<the rpc from the deployment, not a public default>
curl -s -X POST -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' $RPC
# 0x14a34 = 84532 (Base Sepolia / vnet)   0x2105 = 8453 (Base mainnet)

curl -s -X POST -H 'content-type: application/json' \
  --data "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"eth_getCode\",\"params\":[\"$ADDR\",\"latest\"]}" $RPC \
  | head -c 120
```

The `eth_chainId` call is one line and it is the difference between "the
contract is missing" and "I am looking at the wrong network".

## The related trap in the same repo

Two addresses were cited by different documents — the README and the
whitepaper — and **both were deployed**. The older one had an older contract
version whose `burnBps`/`rewardBps` getters revert. A revert on a getter is
not a missing function; it is a different build. Check which document matches
the current deployment before "fixing" an address.
