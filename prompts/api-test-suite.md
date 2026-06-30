# api-test-suite — Prompt for Validating API Keys and Endpoints

## Description

Validates multiple API keys and endpoints in a systematic sweep, documenting
which ones work and which fail with specific error codes.

## The Prompt

```
Validate these API keys and endpoints. For each:
1. Make a test request (use a safe, non-destructive endpoint)
2. Document the response: status code, response body snippet
3. Classify: ✅ Working / ❌ Failed (with error code and reason)

Endpoints to test:
- Exa: POST https://api.exa.ai/search with {query: "test"}
- Firecrawl: GET https://api.firecrawl.dev/v1/scrape with test URL
- Brave: GET https://api.search.brave.com/res/v1/web/search?q=test
- DeepSeek: POST https://api.deepseek.com/chat/completions (minimal request)

Report format:
| Provider | Status | Status Code | Notes |
|----------|--------|-------------|-------|

Rules:
- Don't retry more than once per endpoint
- Note rate limits if encountered
- If 403, check if key needs different permissions
- If connection refused, service may be down
```

## When to Use

- Onboarding new API keys
- Debugging why a service isn't working
- Periodic health checks of integrations

## Last Verified: 2026-06-30
