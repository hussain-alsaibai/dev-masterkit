# Chainable Redaction Wrapper Prompt

Use this prompt when adding a sensitive-data redaction layer in front of an
existing LLM/client API without forcing callers to rewrite their integration.

## Prompt

You are adding a chainable PII redaction utility around an existing chat-style
client.

Implement the smallest wrapper that preserves the caller-facing surface:

- accept the same `.chat({ prompt })` and `.chat({ messages })` shapes,
- redact before forwarding to the wrapped endpoint,
- expose the redaction events without requiring a runtime dependency,
- keep replacement behavior configurable,
- allow selected entity types when the upstream detector supports it,
- bypass redaction cleanly when configured,
- keep credential and region errors explicit,
- resolve overlapping entity ranges deterministically,
- avoid adding a large SDK if the project has a no-new-dependency constraint,
- cover the wrapper with mocked unit tests, not live cloud calls,
- include one runnable example that separates `redact-only` from normal chat.

Prefer a plain adapter/wrapper over changing every endpoint implementation.
The wrapper should be removable, testable in isolation, and boring to call.

## Test Shape

Cover at least:

- entity detection request shape,
- selective entity redaction,
- custom replacement strings,
- missing credentials,
- overlapping ranges,
- prompt input,
- messages input,
- bypass mode,
- event subscription or equivalent callback surface.

Do not require real AWS, Google, Azure, or vendor credentials in unit tests.
Mock the provider response at the narrow HTTP/client boundary.

## Verified Use

This pattern was verified while implementing an AWS Comprehend PII redaction
utility for `arakoodev/EdgeChains`. The implementation added:

- `detectPiiEntities()` and `redact()` helpers with inline AWS SigV4,
- a `Redact` wrapper that sits in front of OpenAI, GeminiAI, LlamaAI, and
  RetellAI-style endpoints,
- 12 focused unit tests,
- a runnable `examples/redact-with-comprehend/` example with `/chat` and
  `/redact-only` routes.

## Last verified: 2026-07-16

- Repo: `hussain-alsaibai/EdgeChains`
- Branch: `ts`
- Commit: `c7bfdae4`
- Verification: `npm test -- awsComprehend.test.ts`, `tsc -b`, and prettier
  completed cleanly before the branch was pushed.
- Blocker: upstream PR creation is still blocked by fine-grained PAT scope
  (`Resource not accessible by personal access token`).
