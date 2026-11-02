# A Fallback Chain Needs A Live Probe Per Entry, Not A Config Read

**A rule for any multi-provider fallback chain, retry ladder, or model
selection list.**

> Found 2026-11-01 and confirmed 2026-11-02 while rebuilding an agent
> runtime's provider chain. **Last verified:** 2026-11-02 — 7 chain entries
> probed with a real completion; 1 answered 429, 4 registered OpenRouter
> models answered 503/404. The dead first hop (`deepseek/deepseek-chat`)
> failed **26 times in a 4-hour window** before it was found.

## The Rule

> **"Registered" and "in the provider's catalog" are both weaker than
> "answered a request". A registered dead model is worse than an unregistered
> one, because the chain looks fuller than it is.**

## The Three-Part Check

A fallback entry is only alive if it passes all three. Steps 1 and 2 are
necessary; **only step 3 counts**.

1. The alias exists in the agent's model list — proves the alias only.
2. The model id is registered under the provider — proves registration.
3. **An actual completion returns 200** — proves callable.

A tool that prints `configured` for every entry has run steps 1 and 2. It has
not run step 3, and it cannot.

## What Step 2 Misses

Two separate defects wore the same costume — "it is configured":

```json
"providers": {
  "deepseek": { "models": [] }          // <- registered as a fallback,
                                         //    but the array is empty
}
```

The provider existed. The API key was valid. A direct probe returned **200 in
1.1s**. Yet every failover died instantly with:

```
Unknown model: deepseek/deepseek-chat. Found
agents.defaults.models["deepseek/deepseek-chat"], but no matching
models.providers["deepseek"].
```

**26 occurrences in one 4-hour window.** Every failover paid this dead hop
first. The chain *looked* repaired — 7 entries, 5 providers — and the first
entry was a corpse.

**An empty `models: []` is a silent killer.** It reads like an intentional
placeholder. No validator compares it against the provider's live catalog. The
chain still lists the model as a fallback.

The other costume: the model is registered, the provider's catalog lists it,
and it still cannot be called.

| model | live probe |
|---|---|
| `deepseek/deepseek-chat` | OK 1.0s |
| `openrouter/dots-studio/dots-3-note-preview:free` | OK 1.0s |
| `minimax/MiniMax-M2.7-highspeed` | OK 2.0s |
| `nvidia/meta/llama-3.2-90b-vision-instruct` | OK 2.1s |
| `openrouter/cohere/north-mini-code:free` | OK 0.4s |
| `google/gemini-3-flash-preview` | OK 1.1s |
| `openrouter/xingchen-agi/xing4.0-29b-a4b:free` | **HTTP 429** (1 of 2 probes) |
| `openrouter/recursive/flint-v1.0:free` | **503** no upstream |
| `openrouter/nvidia/nemotron-3.5-super-vl:free` | **404** guardrail |
| `openrouter/liquid/lfm-2.5-2.6b:free` | **404** guardrail |

Being in a provider's catalog is **neither necessary nor sufficient**. One
NVIDIA key authorised a single hosted function out of an 85-model catalog:
the other registered ids 404'd with *"Function id ... not found"*.

## The Probe Itself Has Two Traps

**Trap 1 — a too-small `max_tokens` produces a false "empty".** Two
OpenRouter models returned `content: None` at `max_tokens=16` and correct
content at 64. Use `max_tokens >= 64` and ask for an exact reply token so you
can tell "returned nothing" from "was not called".

```bash
# One probe per entry. Parse the HTTP status, not just the body.
curl -s -w '\n%{http_code}' \
  -H "Authorization: Bearer $KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"<id>","max_tokens":64,"messages":[{"role":"user","content":"Reply with exactly: OK"}]}' \
  https://<provider-endpoint>/v1/chat/completions
```

**Trap 2 — a probe that succeeds once proves very little.** The last entry
above answered 429 on one of two probes. **Probe twice**, and record the
status each time. A single 200 is evidence; two 200s is a working door.

## Count Providers, Not Entries

A chain of `minimax/M2.7` + `minimax/M2.5` + `minimax/M2.7-highspeed` is
**one provider with three doors**. When minimax entered cooldown there was
no second provider to catch it, and 12 automations auto-disabled after 10
consecutive failures — all reported as `cause: rate_limit`, which pointed at
the wrong thing entirely.

See also `prompts/fail-closed-on-unavailable-data.md` (the general shape) and
`prompts/credential-order-is-not-validity.md` (order is not evidence of
validity — the same error, in the credential resolver).
