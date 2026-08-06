# tiny-prompt — Prompt Templating for AI Agents

> Variable interpolation, chain-of-thought, few-shot, multi-model routing. Zero deps. One file.

**Repo:** https://github.com/hussain-alsaibai/tiny-prompt
**Install:** `pip install tiny-prompt`
**Last verified:** 2026-08-06

---

## What It Does

`tiny-prompt` gives AI agents a structured way to build, compose, and render prompt templates. Variables, conditionals, loops, chain-of-thought chains, few-shot examples, role-based composition, and model-cost-aware routing — all in pure Python.

## Quick Start

### Variable Interpolation

```python
from tiny_prompt import Prompt

p = Prompt("Explain {topic} to a {audience} in {tone} tone.")
rendered = p.render(topic="quantum computing", audience="5th grader", tone="fun")
# Explain quantum computing to a 5th grader in fun tone.
```

### Role-Based Composition

```python
from tiny_prompt import Prompt, Role

p = (
    Prompt.system("You are a {role} assistant.")
    + Prompt.user("Help me with {task}.")
    + Prompt.assistant("I'll help you with {task}.")
    + Prompt.user("What about {followup}?")
)

messages = p.render(role="SQL", task="query optimization", followup="indexes").to_messages()
# [{"role": "system", "content": "..."},
#  {"role": "user",   "content": "..."}, ...]
```

### Conditionals & Loops

```python
from tiny_prompt import Prompt

p = Prompt("""\
{{#if premium}}
Upgrade note: {upgrade_msg}
{{/if}}
{{#each features as feature}}
- {feature}
{{/each}}
""")

print(p.render(
    premium=True,
    upgrade_msg="You have access to 1000 requests/day",
    features=["Fast caching", "Priority support", "Custom domains"]
))
```

### Chain of Thought

```python
from tiny_prompt import Chain

chain = Chain(preamble="Solve this step by step:")
chain.step("Think",    "Given {problem}, identify the key constraint.")
chain.step("Research", "Find relevant patterns from {examples}.")
chain.step("Plan",     "List 3 approaches ranked by {criteria}.")
chain.step("Execute",  "Implement approach {choice}.")
chain.step("Verify",   "Does this solve {problem}?")

rendered = chain.render(problem="slow API", examples="cache patterns", criteria="speed", choice="2")
```

### Few-Shot Examples

```python
from tiny_prompt import Prompt, Example

p = Prompt("Classify this email as spam or not.")
p.add_example(Example(
    input="FREE MONEY!!! Click here now!!!",
    output="spam"
))
p.add_example(Example(
    input="Hi, can we reschedule Thursday's meeting?",
    output="not_spam"
))

print(p.render())
```

### Model Cost-Aware Routing

```python
from tiny_prompt import model_router

router = model_router(
    {
        "gpt-4": {"cost_per_1k": 0.03, "context_window": 128000},
        "gpt-3.5": {"cost_per_1k": 0.002, "context_window": 16385},
    }
)

prompt = Prompt("{task} — be {detail}").render(task="summarize doc", detail="brief")
route = router.select(prompt, max_cost=0.01)
# Returns cheapest model under budget
```

## Key Classes

| Class | Description |
|-------|-------------|
| `Prompt` | Template with variables, conditionals, loops |
| `Chain` | Chain-of-thought step sequencing |
| `Example` | Few-shot example input/output pair |
| `Role` | Role-based message builder (system/user/assistant) |

## When to Use

- Building reusable prompt templates across agent workflows
- Chain-of-thought prompting pipelines
- Few-shot example management
- Model cost optimization via routing
