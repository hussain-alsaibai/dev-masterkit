# Parallel Issue Scoring Pattern

> Native `https.get` + `Promise.all` for high-throughput GitHub API scoring.
> Replaces slow sequential loops when scoring hundreds of candidates.
> **Last verified:** 2026-08-24

## The Problem

Sequential scoring of 250 issues × 3 API calls each = ~750 sequential calls.
At ~100ms each = **75 seconds minimum**, often hanging indefinitely.

## The Fix

Use `Promise.all` with controlled concurrency (batching) to parallelize calls.

### Core: `pMap` — Parallel Map with Concurrency Control

```javascript
async function pMap(items, fn, concurrency = 10) {
  const results = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    results.push(...await Promise.all(batch.map(fn)));
  }
  return results;
}
```

### Core: Async HTTP GET with Token Injection

```javascript
function httpGet(url, token) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'Accept': 'application/vnd.github+json',
        'Authorization': `Bearer ${token}`,
        'X-GitHub-Api-Version': '2022-11-28'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`JSON parse failed: ${data.slice(0, 200)}`)); }
      });
    });
    req.setTimeout(10000, () => { req.destroy(); reject(new Error(`Timeout: ${url}`)); });
    req.on('error', reject);
  });
}
```

### Token Extraction

```javascript
const tokenMatch = stdout.match(/password=(\w+)/);
const token = tokenMatch ? tokenMatch[1] : null;
```

Reads from `~/.git-credentials` via `git config --get credential.helper` + `echo "url=..." | git credential fill`.

### Scoring: Call All 3 APIs in Parallel Per Issue

```javascript
async function scoreOne(issue) {
  const [repo, comments, searchResult] = await Promise.all([
    httpGet(`https://api.github.com/repos/${issue.repo}`, token),
    httpGet(`${issue.comments_url}`, token),
    httpGet(`https://api.github.com/search/issues?q=repo:${issue.repo}+is:pr+state:open`, token)
  ]);

  const competition = searchResult.total_count || 0;
  const stars = repo.stargazers_count || 0;
  // ... scoring logic
}
```

### Concurrency Tuning

- **10 concurrent** is safe for GitHub API (handles rate limits with ~10 req/10s headroom)
- Batch size: 10 items × 3 calls = 30 concurrent HTTPS connections max
- For 250 issues: 25 batches × 10 = ~250 calls in ~25s (vs. 750s sequential)

### Critical: Always Inject the Token

Common bug: `httpGet` helper was defined but the caller was NOT passing `token`.
Every `https.get` call needs the `Authorization` header or the API returns `401`.

```javascript
// ✅ Correct
const [repo, comments, searchResult] = await Promise.all([
  httpGet(url1, token),
  httpGet(url2, token),
  httpGet(url3, token)
]);

// ❌ Wrong — token defined but not used
const repo = await httpGet(url1); // returns 401 on private/external repos
```

### Error Handling

```javascript
try {
  results = await pMap(candidates, scoreOne, 10);
} catch (e) {
  if (e.message.includes('403') || e.message.includes('rate limit')) {
    process.stderr.write(`Rate limited at batch ${i}, pausing...\n`);
    await new Promise(r => setTimeout(r, 60000));
    // retry this batch
  }
}
```

## Key Metrics

| Metric | Before | After |
|--------|--------|-------|
| Scan time (250 issues) | ~10 min (hanging) | ~25 seconds |
| Concurrent calls | 1 | 10 |
| Token injection | Missing (401s) | Fixed |

## When to Use

- **Use:** Scoring hundreds of GitHub issues/PRs/candidates
- **Use:** Multiple independent API calls per item
- **Avoid:** Sequential dependency chains (call B depends on A)
- **Avoid:** Tight loops without concurrency limits (causes 429 rate limits)

## Related

- `prompts/bounty-pat-fine-grained-fixes.md` — Fine-grained PAT scope requirements for cross-repo access
- `skills/bounty-scanner/` — Live implementation of this pattern
