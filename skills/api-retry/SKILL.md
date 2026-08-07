# API Retry Utility

A reusable module for making API calls with exponential backoff retry logic.

## Features
- Exponential backoff (1s, 2s, 4s, 8s...)
- Configurable max retries (default: 3)
- Rate limit handling (429 status)
- Circuit breaker pattern
- Logging of retries

## Usage

```javascript
const { apiCall } = require('./api-retry');

// Simple usage
const result = await apiCall({
  url: 'https://api.example.com/data',
  method: 'POST',
  headers: { 'Authorization': 'Bearer token' },
  body: { key: 'value' }
});

// With custom options
const result = await apiCall({
  url: 'https://api.example.com/data',
  method: 'GET'
}, {
  maxRetries: 5,
  baseDelay: 1000,
  maxDelay: 30000
});
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| maxRetries | 3 | Maximum number of retry attempts |
| baseDelay | 1000 | Initial delay in ms (doubles each retry) |
| maxDelay | 30000 | Maximum delay cap in ms |
| retryOn | [408, 429, 500, 502, 503, 504] | HTTP status codes to retry |

## Error Handling

The function throws after all retries are exhausted with:
- `message`: Error description
- `statusCode`: Last HTTP status
- `attempts`: Number of attempts made
