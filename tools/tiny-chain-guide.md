# tiny-chain Guide

> Streaming LLM processor with retries, fallbacks, function calling, and JSON extraction. ~600 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-chain
**Last Verified:** 2026-07-22

## Quick Start

```python
from tiny_chain import Chain

chain = Chain(api_key="sk-...", model="gpt-4o-mini", max_retries=3)
response = chain.complete("Explain quantum entanglement in one sentence.")
print(response.content)
```

## Key Patterns

| Pattern | API |
|---------|-----|
| **Streaming** | `for chunk in chain.stream(prompt): print(chunk.content, end="")` |
| **Model fallbacks** | `chain.complete_with_fallback("gpt-4o", ["gpt-4o-mini", "gpt-3.5-turbo"], prompt)` |
| **Function calling** | `chain.complete(prompt, functions=[weather_func])` |
| **JSON extraction** | `json_extractor.extract_json(text)` |
| **Structured output** | `structured_output(prompt, schema)` |

## Cost Tracking

Every response includes `usage.total_tokens` and `usage.cost_usd` using built-in price tables. Override `_cost_per_1k_tokens` for custom models.

## When to Use

- **tiny-chain** → streaming + retries + structured output without LangChain/LlamaIndex overhead
- **tiny-mcp** → exposing tools via MCP protocol instead of direct function calls

## See Also

- [tiny-memory Guide](tiny-memory-guide.md) — persistent agent memory
- [tiny-workflow Guide](tiny-workflow-guide.md) — DAG orchestration for multi-step chains
