# tiny-stream — Streaming Response Parser for LLM APIs

## Repo
https://github.com/hussain-alsaibai/tiny-stream

## One-liner
Zero-dep streaming response parser for LLM APIs — SSE, JSON-lines, and chunked transfer decoding.

## Install
```bash
pip install tiny-stream
```

## Quick Example
```python
from tiny_stream import stream_openai, stream_anthropic

# Parse OpenAI SSE stream
async for token in stream_openai(response):
    print(token, end="", flush=True)

# Parse Anthropic SSE stream
async for token in stream_anthropic(response):
    yield token
```

## Key Features
- **SSE parsing** — handles `data: ...\n\n` format with JSON parsing
- **JSON-lines** — newline-delimited JSON objects
- **Chunked transfer** — handles `Transfer-Encoding: chunked`
- **Async iterators** — memory-efficient token-by-token yielding
- Zero dependencies, stdlib only

## When to Use
- Any LLM API call with `stream=True`
- Parsing SSE endpoints from OpenAI, Anthropic, Ollama, Groq, etc.
- Combine with tiny-realtime for end-to-end streaming pipelines

## Related
- **tiny-realtime** — SSE emitting + WS routing for AI streaming UIs
- Together they form a complete streaming stack: parse → route → deliver

## Last Verified: 2026-07-26
- Repo: tiny-stream (created 2026-07-25)
- Status: Initial commit, no starred activity
