# Tool Guide: agent-security-patterns-2026

> **Last verified:** 2026-08-16
> **Repo:** https://github.com/hussain-alsaibai/agent-security-patterns-2026
> **License:** MIT

## What it is

A comprehensive technical guide to securing autonomous AI agents. Covers the agent-specific threat model, attack taxonomy, and battle-tested defense patterns. Markdown-based knowledge base — no code to run.

## When to use

- Designing agent security architecture
- Reviewing an agent codebase for vulnerabilities
- Understanding prompt injection, tool poisoning, resource exhaustion
- Selecting defense patterns for a production agent

## Key sections

| Section | Contents |
|---------|----------|
| Agent Threat Model | 4-axis model: confidentiality, integrity, availability, + autonomy misuse |
| Attack Taxonomy | Prompt injection, data/tool poisoning, resource exhaustion, exfiltration |
| Defense Patterns | Input sanitization, output filtering, tool vetting, budget gates, sandboxing |
| Security Tooling | MCP auth, secret scanning, rate limiting, observability |

## Quick reference

```
Traditional AppSec                    Agent Threat Model
─────────────────                    ───────────────────
Confidentiality: data leaks          + Indirect data leaks (via LLM output)
Integrity: code injection             + Instruction injection
Availability: DoS                    + Resource exhaustion
                                      + Autonomy misuse
                                      + Tool poisoning
```

## Related tools

- `tiny-tracer` — distributed tracing for agent pipelines
- `tiny-circuit-breaker` — protect against cascade failures
- `security-sentinel` skill — workspace security scanning
