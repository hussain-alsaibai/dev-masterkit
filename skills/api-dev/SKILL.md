# api-dev — Skill for API Development

## Trigger

Use when the user asks to:
- "Create an API" or "build REST endpoints"
- "Test this API" or "debug API calls"
- "Generate OpenAPI spec" or "document API"
- "Mock an external API" for development
- "Load test endpoints"

## Description

Build, test, document, and debug HTTP APIs using only standard tools (curl, Python stdlib). Covers the full API lifecycle: scaffolding endpoints, testing with curl, generating OpenAPI docs, mocking services, and debugging.

## Procedure

### 1. Scaffold API Endpoints

Choose your stack:

**Python (stdlib only):**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/users':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"users": []}).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        # Process data...
        self.send_response(201)
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), APIHandler)
    server.serve_forever()
```

**Testing with curl:**
```bash
# GET request
curl -s http://localhost:8000/users | jq .

# POST JSON
curl -s -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# With headers
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  http://localhost:8000/users
```

### 2. Test API Endpoints

**Validate status codes and response format:**
```bash
# Check status code
curl -s -o /dev/null -w "%{http_code}" http://api.example.com/health

# Full response with headers
curl -si http://api.example.com/health

# Save response to file
curl -s http://api.example.com/data > response.json
```

**Python test client (stdlib):**
```python
import urllib.request
import json

# GET
with urllib.request.urlopen('http://api.example.com/users') as resp:
    data = json.loads(resp.read())

# POST
req = urllib.request.Request(
    'http://api.example.com/users',
    data=json.dumps({"name": "Alice"}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as resp:
    print(resp.status)
```

### 3. Generate OpenAPI Spec

```python
# openapi_spec.py — generates spec from docstrings
import json
import inspect

spec = {
    "openapi": "3.0.0",
    "info": {"title": "My API", "version": "1.0.0"},
    "paths": {}
}

def add_endpoint(path, method, summary, params=None, responses=None):
    if path not in spec["paths"]:
        spec["paths"][path] = {}
    spec["paths"][path][method] = {
        "summary": summary,
        "parameters": params or [],
        "responses": responses or {"200": {"description": "OK"}}
    }

# Add your endpoints
add_endpoint("/users", "get", "List all users")
add_endpoint("/users", "post", "Create a user")

print(json.dumps(spec, indent=2))
```

### 4. Mock External APIs

```python
# mock_server.py — intercept and mock responses
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            '/api/users': {"users": [{"id": 1, "name": "Mock User"}]},
            '/api/health': {"status": "ok"}
        }
        response = routes.get(self.path, {"error": "Not found"})
        status = 200 if self.path in routes else 404
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# Run: python mock_server.py
```

### 5. Debug API Issues

```bash
# Verbose output (show request/response details)
curl -v http://api.example.com/endpoint

# Time breakdown
curl -w "@curl-format.txt" -o /dev/null -s http://api.example.com/endpoint

# Where curl-format.txt contains:
# time_namelookup: %{time_namelookup}\n
# time_connect: %{time_connect}\n
# time_appconnect: %{time_appconnect}\n
# time_pretransfer: %{time_pretransfer}\n
# time_redirect: %{time_redirect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total: %{time_total}\n

# Check SSL certificate
curl -vI https://api.example.com 2>&1 | grep "SSL\|TLS"

# Follow redirects
curl -L -s http://bit.ly/xxx
```

## Checklist

- [ ] API responds with correct status codes (200, 201, 400, 404, 500)
- [ ] Content-Type headers are set correctly
- [ ] JSON responses are valid and parseable
- [ ] Error responses include helpful messages
- [ ] Authentication headers work as expected
- [ ] Rate limiting is handled gracefully
- [ ] CORS headers are configured if needed

## Examples

**Full REST API (Python stdlib):**
```python
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

users = []

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == '/users':
            self._send_json({"users": users})
        elif self.path.startswith('/users/'):
            user_id = int(self.path.split('/')[-1])
            user = next((u for u in users if u['id'] == user_id), None)
            if user:
                self._send_json(user)
            else:
                self._send_json({"error": "Not found"}, 404)
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == '/users':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            data['id'] = len(users) + 1
            users.append(data)
            self._send_json(data, 201)
        else:
            self._send_json({"error": "Not found"}, 404)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), APIHandler)
    print("API running on http://localhost:8000")
    server.serve_forever()
```

## See Also

- `api-test-suite.md` — Prompt for systematic API validation
- `skills/api-validation/SKILL.md` — API key and endpoint testing
- `skills/test-automation/SKILL.md` — Generate test suites

---

*Last verified: 2026-06-26*
