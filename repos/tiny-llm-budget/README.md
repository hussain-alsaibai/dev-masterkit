# tiny-llm-budget

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](tiny_llm_budget.py)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/hussain-alsaibai/tiny-llm-budget)

The smallest reliable way to know whether a prompt + completion will fit an LLM's context window **before** you call the API. Single-file, zero-dep, ~290 LOC.

## Why?

Calling a frontier model with a prompt that overflows the context window either silently truncates (and you lose data) or hard-fails (and you lose the call's cost). Most teams re-implement the "count tokens" check per-service. `tiny-llm-budget` does it once.

## Install

```bash
pip install tiny-llm-budget
# optional, for exact OpenAI token counts:
pip install tiktoken
```

## Quick start

```python
from tiny_llm_budget import plan

b = plan("gpt-4o", system="You are a helpful assistant.", user="hi", expected_completion=800)
print(b.fits)            # True
print(b.total_tokens)    # 814
print(b.remaining)       # 127186
print(b.to_dict())
# {"model": "gpt-4o", "max_tokens": 128000, "total_tokens": 814, ...}

if not b.fits:
    raise ValueError(f"prompt overflows by {-b.remaining} tokens — truncate first")
```

## Token counting strategies

| Family | Strategy | Accuracy |
|--------|----------|----------|
| OpenAI (`gpt-*`, `o1-*`, `o3-*`, `o4-*`) | `tiktoken` if installed, else heuristic | Exact with tiktoken; ±15% without |
| Anthropic (`claude-*`) | 3.5 chars/token + 1.1x safety | ±10% |
| Everyone else | 4 chars/token + 1.15x safety | ±15% |

The output is a *budget* number, not a *billing* number. Always cross-check the API's reported `usage.prompt_tokens` for billing.

## Conversation history

```python
from tiny_llm_budget import plan

b = plan(
    "gpt-4o",
    system="You are a translator.",
    history=[
        ("user", "Translate to French: hello"),
        ("assistant", "bonjour"),
        ("user", "And to Spanish?"),
    ],
    user="",  # last user msg already in history
    expected_completion=200,
    safety_margin=0.05,  # keep 5% headroom
)
```

## Fine-tunes and self-hosted models

```python
from tiny_llm_budget import plan, register_model

# Option 1: per-call
plan("my-fine-tune", user="hi", model_limits={"my-fine-tune": 16384})

# Option 2: globally
register_model("my-fine-tune", 16384)
plan("my-fine-tune", user="hi")
```

## Model catalogue (2026-Q4)

OpenAI: gpt-4o / 4o-mini / 4-turbo / 4 / 3.5-turbo, o1-preview / o1-mini  
Anthropic: claude-3-5-sonnet / 3-5-haiku / 3-opus / 3-sonnet / 3-haiku  
Google: gemini-1.5-pro / 1.5-flash / 2.0-flash-exp  
Meta: llama-3.1-{405b, 70b, 8b}  
Mistral: mistral-large-2, mixtral-8x22b  
DeepSeek: deepseek-v3

Unknown models default to 8k (conservative).

## Public API

- `count_tokens(text, model="gpt-4o") -> int`
- `plan(model, *, system, user, history, expected_completion, tools_tokens, safety_margin, model_limits) -> Budget`
- `Budget(model, max_tokens, total_tokens, remaining, fits, segments, strategy)`
- `Segment(name, text, tokens)`
- `MODEL_LIMITS` (dict, mutable)
- `register_model(name, max_tokens)`


## v0.2.0 — compare_models() + cost catalogue

```python
from tiny_llm_budget import compare_models, COST_PER_MILLION

results = compare_models(
    ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"],
    system="You are a helpful assistant.",
    user=user_message,
    history=[("user", prev_user), ("assistant", prev_resp)],
    expected_completion=500,
    cost_per_million=COST_PER_MILLION,
)

for model, budget, cost in results:
    print(f"{model}: fits={budget.fits} remaining={budget.remaining} cost=${cost}")
```

Returns a list sorted by `fits` (desc), then `remaining` (desc), then
`cost` (asc). The first tuple is the recommended pick. Pass a custom
`cost_per_million={name: (in, out)}` dict to override the embedded
catalogue — useful for negotiated enterprise rates or new releases.

## Licence

MIT
