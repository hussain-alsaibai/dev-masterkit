# tiny-realtime — SSE + WebSocket Helpers for AI Streaming

## Repo
https://github.com/hussain-alsaibai/tiny-realtime

## One-liner
Zero-dep SSE and WebSocket helpers for AI agent streaming responses. Handles SSE emit, AI token chunk buffering, and WS routing.

## Install
```bash
pip install tiny-realtime
```

## Key Components
- **`SSEEmitter`** — send `data: ...\n\n` events with auto content-type and proper headers
- **`AIStreamer`** — buffer and yield LLM token chunks as SSE/WS streams
- **`SSEClient`** — async context manager for consuming SSE endpoints
- **`WSApp`** — WebSocket router with `send_text / send_json / send_bytes`

## SSE Example
```python
from tiny_realtime import SSEEmitter

async def stream_llm_response(prompt: str, emitter: SSEEmitter):
    async for chunk in llm.stream(prompt):
        await emitter.emit(chunk)  # sends data: <chunk>\n\n
    await emitter.done()  # closes the stream
```

## WebSocket Router Example
```python
from tiny_realtime import WSApp

app = WSApp()

@app.websocket("/ws/chat")
async def chat(ws):
    async for msg in ws:
        response = await process(msg)
        await ws.send_json({"reply": response})
```

## When to Use
- Any LLM UI that streams tokens to the browser
- Webhook receivers that need to push updates to clients
- Agent dashboards with real-time status updates

## Last Verified: 2026-07-26
- Repo: tiny-realtime (created 2026-07-26)
- Status: Initial commit, no starred activity
