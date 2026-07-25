# tiny-stream Guide

> Streaming response parser for LLM APIs — SSE, JSON-lines, chunked transfer.

## Overview
`tiny-stream` parses streaming HTTP responses (SSE, JSON-lines, chunked transfer) from LLM APIs. Zero dependencies, one file.

**Repo:** https://github.com/hussain-alsaibai/tiny-stream
**Last verified:** 2026-07-25

## Quick Start

```python
from tiny_stream import StreamParser

parser = StreamParser()
async for event in parser.parse(response):
    print(event.delta)  # or event.text, event.tool_call, etc.
```

## Use When
- Parsing OpenAI/Anthropic SSE streams
- Handling JSON-lines (`data: {...}\ndata: {...}`) responses
- Consuming chunked Transfer-Encoding responses
- Building LLM response renderers or UI streaming

## Key Patterns
- **SSE events:** Parses `data: message\n\n` format, handles `[DONE]` sentinel
- **JSON-lines:** Splits on `\n`, skips empty/binary chunks
- **Chunked transfer:** Reassembles HTTP chunked encoding
- **Delta extraction:** Normalizes across provider formats (OpenAI, Anthropic, generic)

## See Also
- `tiny-workflow` — workflow orchestration with streaming steps
- `tiny-mem` — memory that can consume streaming deltas
