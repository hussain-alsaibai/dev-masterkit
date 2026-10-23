# tiny-stream Guide

## Repo
https://github.com/hussain-alsaibai/tiny-stream

## What It Does

Zero-dependency streaming parser for LLM responses. One file, no setup. Handles
SSE and JSONL wire formats and normalises tokens across providers.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_stream import
stream_openai, stream_anthropic`. **Neither function exists.** Verified against
upstream `tiny_stream.py`:

```
__all__ = ['StreamParser', 'LLMStream', 'SSEEvent', 'ParsedToken', 'StreamFormat']
```

Top-level names: `StreamParser`, `LLMStream`, `SSEEvent`, `ParsedToken`,
`StreamFormat`.

The provider-specific helpers were replaced by a **format-agnostic** parser:
one `StreamParser` handles both SSE and JSONL, and `LLMStream` normalises the
output.

## Key Features

- `StreamParser` — parses SSE blocks and JSONL lines into tokens
- `LLMStream` — provider-agnostic normalised stream
- `SSEEvent` / `ParsedToken` — the parsed value objects
- `StreamFormat` — selects the wire format

## Quick Start

```python
from tiny_stream import StreamParser, LLMStream, StreamFormat

parser = StreamParser(format=StreamFormat.SSE)
for token in parser.feed(sse_chunk):
    print(token.text, end="")

stream = LLMStream(source=response.iter_bytes(), format=StreamFormat.SSE)
for token in stream:
    print(token.text, end="")
```

## When to Use

- Consuming streaming LLM responses without an SDK
- Normalising token output across providers that use different wire formats
- Agent pipelines that need incremental parsing rather than a full buffer

## Related

- `tools/tiny-chain-guide.md` — `TinyChain`, retries and fallbacks over a stream
- `tools/tiny-router-guide.md` — SSE server-side responses
