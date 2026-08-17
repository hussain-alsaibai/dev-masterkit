# tiny-context Guide

> LLM Context Window Manager — Zero dependencies, ~14 KB single file.
> Last verified: 2026-08-17 | Version 0.1.0 | hussain-alsaibai/tiny-context

## What it does

`tiny-context` solves the four problems every LLM app hits in production:

1. **Budgeting** — fit a prompt into N tokens without guessing
2. **Truncation** — drop least-important chunks when over budget
3. **Compression** — summarize on the fly with pluggable strategies
4. **Routing** — pick the right model tier based on context length and cost

## Install

```bash
pip install tiny-context
```

Or just copy `tiny_context.py` into your project — single file, zero dependencies.

## Core Concepts

### Budget

```python
from tiny_context import Budget

b = Budget(max_tokens=8192, reserve_for_completion=1000, safety_margin=0.05)
# b.effective_input() == 6784  (room for model's response + 5% overhead)
```

### Context

```python
from tiny_context import Context, Budget, select_model

ctx = Context(
    model=select_model(required_tokens=4000, prefer="gpt-4o-mini").name,
    budget=Budget(max_tokens=4096, reserve_for_completion=500),
)

ctx.add_system("You are a helpful assistant with access to company docs.")
ctx.add_user("What is the PTO policy for Bahrain employees?")

# Retrieved docs (RAG, tool outputs, anything)
ctx.add_block("retrieved", retrieved_text, importance=0.8)

messages = ctx.render_messages()  # auto-fits to budget
```

### Model Routing

```python
from tiny_context import select_model

# Pick cheapest model that fits N tokens and stays under cost limit
model_info = select_model(
    required_tokens=4000,
    prefer="gpt-4o-mini",      # prefer this tier if it fits
    max_cost_per_1k=0.50,      # hard cost ceiling
)
print(model_info.name)         # e.g. "gpt-4o-mini"
print(model_info.context_limit)  # e.g. 128000
```

`DEFAULT_MODELS` registry includes: gpt-5, gpt-4o, gpt-4o-mini, claude-opus-4, claude-sonnet-4, claude-haiku-4, gemini-2.5-flash, llama-3.3-70b, qwen-2.5-72b, and more.

### Importance-Aware Fitting

```python
# When budget is tight, the fitter drops content in this order:
# 1. Low-importance blocks (importance=0.0–0.3)
# 2. Truncate messages (starting from oldest)
# 3. Drop entire messages from the middle
# 4. Drop low-importance blocks entirely

ctx.add_block("scratchpad", scratch_text, importance=0.2)   # first to go
ctx.add_block("retrieved", docs_text, importance=0.8)        # kept until the end
ctx.add_block("system_reminder", reminder, importance=0.9)    # almost never dropped
```

### Pluggable Compression

```python
from tiny_context import head_tail_compressor  # default — keeps head + tail

ctx = Context(
    model="gpt-4o-mini",
    budget=Budget(max_tokens=4096),
    compressor=head_tail_compressor,  # or your own LLM-backed summarizer
)
```

## Key API

| Symbol | Purpose |
|--------|---------|
| `Budget(max_tokens, reserve_for_completion, safety_margin)` | Token budget with safety buffer |
| `Context(model, budget, tokenizer, compressor)` | Assemble a context window |
| `ctx.add_system(text)` | System prompt (never dropped) |
| `ctx.add_user(text)` | User message |
| `ctx.add_assistant(text)` | Assistant message |
| `ctx.add_block(name, text, importance)` | Named block with importance score |
| `ctx.render_messages()` | Fit and return OpenAI/Anthropic-format messages |
| `select_model(required_tokens, prefer, max_cost_per_1k)` | Route to cheapest-fiting model |
| `DEFAULT_MODELS` | Dict of known models with context limits and costs |

## Test coverage

24 tests, all passing. Run with:
```bash
pytest tiny_context.py -v
```

## Ecosystem

Part of the `tiny-*` zero-dependency ecosystem. See also:
- [tiny-router](tiny-router-guide.md) — WSGI HTTP router with async + Depends()
- [tiny-log](tiny-log-guide.md) — Structured logging
- [tiny-chain](tiny-chain-guide.md) — Streaming LLM processor

## GitHub

https://github.com/hussain-alsaibai/tiny-context
