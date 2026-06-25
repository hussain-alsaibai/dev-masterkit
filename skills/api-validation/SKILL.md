# api-validation — Skill for Testing API Keys and Endpoints

## Trigger

Use when the user asks to:
- "Test this API key"
- "Is this API working?"
- "Validate my credentials"
- "Check if [service] is up"
- "Debug why [integration] is failing"

## Description

Systematically validates API keys and endpoints with safe, non-destructive test
requests. Documents which services work, which fail, and why.

## Procedure

### 1. Gather Credentials

Collect:
- API key/token
- Base URL
- Required headers (Authorization format, Content-Type, custom headers)
- Safe test endpoint (read-only, no side effects)

### 2. Determine Test Strategy

| Service Type | Safe Test Endpoint |
|-------------|-------------------|
| Search API | `GET /search?q=test` or `POST /search` with harmless query |
| AI/LLM API | `POST /chat/completions` with minimal message |
| Scraping API | `GET /scrape` with example.com or similar |
| Storage API | `GET /buckets` or `GET /list` (read-only) |
| Payment API | `GET /balance` or `GET /invoices` (never POST/charge) |

### 3. Execute Test Request

```bash
# Example: Generic API test
curl -s -w "\nHTTP_CODE: %{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "$BASE_URL/safe-endpoint"
```

For POST requests:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 1}' \
  "$BASE_URL/search"
```

### 4. Interpret Response

| Status | Meaning | Action |
|--------|---------|--------|
| 200 OK | Working | ✅ Log as verified |
| 401 Unauthorized | Key invalid or expired | ❌ Check key, regenerate if needed |
| 403 Forbidden | Key valid but lacks permissions | ⚠️ Check scope/subscription level |
| 404 Not Found | Wrong endpoint or deprecated API | ❌ Check docs for current endpoint |
| 429 Too Many Requests | Rate limited | ⏳ Wait and retry with backoff |
| 500+ | Server error | ⏳ Retry later; service issue |
| Connection refused | Service down or wrong URL | ❌ Check URL, DNS, firewall |

### 5. Document Results

Create a validation log:

```markdown
# API Validation Report — YYYY-MM-DD

| Provider | Endpoint | Status | Code | Notes |
|----------|----------|--------|------|-------|
| Exa | /search | ✅ Working | 200 | Response: {...} |
| Firecrawl | /v1/scrape | ✅ Working | 200 | Full HTML returned |
| Brave | /res/v1/web/search | ❌ Failed | 403 | Key lacks search scope |
| DeepSeek | /chat/completions | ✅ Working | 200 | Model: deepseek-chat |
```

### 6. Handle Failures

For 403 errors:
1. Check key permissions in provider dashboard
2. Verify subscription tier supports the endpoint
3. Try alternative auth header format (Bearer vs X-API-Key)

For connection errors:
1. Test DNS resolution: `nslookup api.provider.com`
2. Test with IP directly if DNS fails
3. Check if behind VPN/proxy

## Validation Checklist

- [ ] Test request is read-only and safe
- [ ] Auth headers match provider's documented format
- [ ] Response status and body documented
- [ ] Failures include specific error codes
- [ ] Rate limits noted if encountered
- [ ] Results stored for reference
- [ ] Provider dashboard checked for key status

## Notes

- Never use POST/PUT/DELETE for validation — only GET or safe POST
- Some providers return 200 with an error in the JSON body — always parse the response
- API keys in env vars are safer than hardcoded; never log the full key
- Document the exact header format that worked — providers vary (Bearer, X-API-Key, etc.)

## Last Verified: 2026-06-25
