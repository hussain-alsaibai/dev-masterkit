# tiny-http — Zero-Dependency HTTP Server

## Repo
https://github.com/hussain-alsaibai/tiny-http

## What It Does

Zero-dependency HTTP server for Python. One file, no setup. Handles routing, JSON payloads, file uploads, and streaming responses.

## When to Use

- Standalone microservice without Flask/FastAPI overhead
- Embedding a lightweight HTTP interface in any Python script
- Prototyping API endpoints quickly

## Key Features

- Pure stdlib: `http.server`, `socketserver`, `json`, `urllib`
- Route decorators for GET/POST/PUT/DELETE
- Built-in JSON serialization/deserialization
- Request/response middleware hooks
- CORS headers support
- File upload handling

## Quick Start

```python
from tiny_http import serve, json_response

@serve.get("/health")
def health(req):
    return json_response({"status": "ok"})

@serve.post("/process")
def process(req):
    data = req.json()
    return json_response({"result": data["input"] * 2})

serve(host="0.0.0.0", port=8000)
```

## Last Verified
2026-07-23
