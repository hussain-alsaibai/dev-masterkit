# tiny-llm Tool Guide

> Unified LLM client for Python — zero dependencies, every major provider. OpenAI, Anthropic, Google Gemini, xAI Grok, Ollama.

**Source:** [hussain-alsaibai/tiny-llm](https://github.com/hussain-alsaibai/tiny-llm)
**License:** MIT | **Language:** Python | **Last verified:** 2026-07-31

## When to use

- Single code base calling multiple LLM providers
- Need streaming, retry, cost tracking, and function calling
- Zero-dependency constraint — no pip install chains
- Prototype that needs to swap models easily

## Quick Start

```python
from tiny_llm import LLM

client = LLM()  # auto-detects model from model param

# Basic chat
response = client.chat(model="gpt-4o", messages=[
    {"role": "user", "content": "Summarize this: " + text}
])

# Streaming
for token in client.chat_stream(model="claude-sonnet-4-20250514", messages=[...]):
    print(token, end="", flush=True)

# Function calling
response = client.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=[{"type": "function", "name": "get_weather", "parameters": {...}}]
)

# Cost tracking
print(client.session_cost)  # total USD spent this session
print(response.usage)       # per-call token + cost breakdown

# Model fallback chain
response = client.chat(
    model="gpt-4o",
    messages=[...],
    fallback_models=["claude-sonnet-4-20250514", "gemini-2.0-flash"]
)
```

## Providers

| Provider | Model prefix | Notes |
|----------|-------------|-------|
| OpenAI | `gpt-`, `o1-`, `o3-` | Default, needs `OPENAI_API_KEY` |
| Anthropic | `claude-` | Needs `ANTHROPIC_API_KEY` |
| Google | `gemini-`, `gemma-` | Needs `GEMINI_API_KEY` |
| xAI Grok | `grok-` | Needs `XAI_API_KEY` |
| Ollama | any local model | Needs Ollama running locally |

## Key Features

- **Single interface** — `.chat()` works across all providers
- **Streaming** — `.chat_stream()` yields tokens
- **Function calling** — unified `tools=[]` schema
- **Retry + backoff** — exponential on 429/5xx
- **Cost tracking** — per-call + session aggregate
- **Fallback chains** — try next model if primary unavailable
- **System templates** — parameterized system prompts

## Zero Dependency

Stdlib only — no `openai`, `anthropic`, `google-generativeai` packages. Copy the single file anywhere.

## See Also

- [tiny-agent](https://github.com/hussain-alsaibai/tiny-agent) — agent framework using tiny-llm
- [tiny-chain](tiny-chain-guide.md) — LLM processing pipeline
- [tiny-memory](tiny-memory-guide.md) — agent memory layer
