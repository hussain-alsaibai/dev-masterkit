# Agent Boundary Contracts Prompt

Use this prompt when generated agent output is about to become a real external
side effect: webhook callbacks, tool calls, job queues, API writes, billing
events, or stateful automation.

## Prompt

You are hardening an autonomous-agent boundary where untrusted, generated, or
remote input can trigger real side effects.

Before writing code, identify the boundary and make the contract explicit:

- authentication or signature verification,
- request or job identity,
- idempotency and replay behavior,
- rate limits and abuse limits,
- input schema validation,
- clear error responses,
- structured logs with correlation IDs,
- `/health`, `/ready`, or equivalent status checks,
- timeout, TTL, and cleanup behavior,
- tests for duplicate, invalid, expired, and unauthorized requests.

Implement the smallest contract that makes the boundary safe to operate. Prefer
stdlib-only mechanisms when the project is a tiny-* or zero-dependency repo.
Avoid broad rewrites; add the contract at the edge and cover it with focused
tests.

## Verified Use

This pattern was verified while adding `examples/agent_callback_receiver.py` to
`tiny-router`, with auth, request IDs, rate limiting, TTL idempotency, JSON
validation, `/health`, `/ready`, `/status`, structured logs, and example tests.

## Last verified: 2026-07-13

- Repo: `hussain-alsaibai/tiny-router`
- Commit: `902691d`
- Verification: 15 core tests + 11 callback receiver example tests passing.
