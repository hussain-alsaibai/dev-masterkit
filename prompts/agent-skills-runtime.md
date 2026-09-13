# agent-skills-runtime — Prompt for Building SKILL.md Executable Bundles

## Description

Creates a discoverable, dispatchable Agent Skill bundle (Anthropic-style SKILL.md) backed by a zero-dep Python runtime. Inspired by `tiny-agentskills` and the broader Agent Skills pattern (175K★ ecosystem as of Q3 2026).

## The Prompt

```
Build an Agent Skill bundle called {skill_name} that does {purpose}.

Bundle structure:
  skills/{skill_name}/SKILL.md
  skills/{skill_name}/scripts/   (optional Python helpers)
  skills/{skill_name}/examples/  (1-2 worked examples)

SKILL.md must have YAML frontmatter:
  ---
  name: {skill_name}
  description: {one-sentence trigger summary}
  triggers: ["{phrase 1}", "{phrase 2}", ...]
  ---

SKILL.md body sections (in this order):
  1. ## Description — what the skill does in 2-3 sentences
  2. ## When to Use — concrete trigger phrases the agent matches
  3. ## The Procedure — numbered steps the agent follows verbatim
  4. ## Examples — at least one worked call/output pair
  5. ## Pitfalls — known failure modes and how to avoid them
  6. Last verified: YYYY-MM-DD

Runtime requirements:
  - Zero third-party deps (stdlib only)
  - If runtime is Python, use `tiny-agentskills` registry pattern
  - Each procedure step must end on a checkable completion criterion
  - Every trigger must appear in at least one example

Verification:
  - Triggers all match (substring/case-insensitive) the procedure
  - At least one example exercises each step
  - Last verified date is set to today
```

## When to Use

- Packaging expertise into a SKILL.md bundle for an agent fleet
- Migrating a documented runbook into an executable skill
- Authoring skills for the 175K★ Agent Skills ecosystem
- Building a skills marketplace runtime

## Tested In

- `tiny-agentskills` v0.1.0 (hussain-alsaibai/tiny-agentskills) — Sept 2026
- dev-masterkit repo authoring workflow

**Last verified:** 2026-09-11
