# TypeScript Vector DB SDK Pattern — Qdrant Implementation

**Created:** 2026-08-11
**Last verified:** 2026-08-11
**Author:** OpenClaw / hussain-alsaibai
**Source:** Real implementation for arakoodev/EdgeChains issue #273

---

## Overview

This pattern documents a clean TypeScript SDK for Qdrant vector database. Built for the EdgeChains JS/TS SDK bounty, but reusable for any TypeScript project needing Qdrant integration.

---

## Architecture

### Clean Class Design

```typescript
class Qdrant {
  private baseUrl: string;
  private apiKey?: string;
  private maxRetries: number;

  constructor(config: QdrantConfig) {
    this.baseUrl = config.url.replace(/\/$/, '');
    this.apiKey = config.apiKey;
    this.maxRetries = config.maxRetries ?? 5;
  }
}
```

### Config Shape

```typescript
interface QdrantConfig {
  url: string;           // e.g., "http://localhost:6333"
  apiKey?: string;       // Optional API key
  maxRetries?: number;   // Default: 5
  timeout?: number;      // Request timeout in ms
}
```

---

## Exponential Backoff Retry

Every HTTP call wraps in retry logic:

```typescript
private async request<T>(
  method: string,
  path: string,
  body?: object,
  retries = this.maxRetries
): Promise<T> {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await this.executeRequest<T>(method, path, body);
    } catch (err) {
      if (attempt === retries) throw err;
      const delay = Math.min(1000 * 2 ** (attempt - 1), 10000);
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error('unreachable');
}
```

Key: exponential backoff with 10s cap, configurable retry count.

---

## Filter Builder Pattern

Build complex Qdrant filters with a chainable builder:

```typescript
class FilterBuilder {
  private conditions: FilterCondition[] = [];

  must(...conditions: FilterCondition[]): this {
    this.conditions.push({ type: 'must', conditions });
    return this;
  }

  should(...conditions: FilterCondition[]): this {
    this.conditions.push({ type: 'should', conditions });
    return this;
  }

  mustNot(...conditions: FilterCondition[]): this {
    this.conditions.push({ type: 'must_not', conditions });
    return this;
  }

  // Field match conditions
  match(key: string, value: string | number | boolean): FilterCondition {
    return { key, match: { value } };
  }

  range(key: string, opts: { gt?, gte?, lt?, lte? }): FilterCondition {
    return { key, range: opts };
  }

  text(key: string, text: string): FilterCondition {
    return { key, match: { text } };
  }

  keyword(key: string, value: string): FilterCondition {
    return { key, match: { keyword: value } };
  }

  build(): object {
    return {
      must: this.conditions.filter(c => c.type === 'must').flatMap(c => c.conditions),
      should: this.conditions.filter(c => c.type === 'should').flatMap(c => c.conditions),
      must_not: this.conditions.filter(c => c.type === 'must_not').flatMap(c => c.conditions),
    };
  }
}

// Usage:
const filter = new FilterBuilder()
  .must(
    new FilterBuilder().match('status', 'active'),
    new FilterBuilder().range('score', { gte: 0.8 })
  )
  .should(new FilterBuilder().match('tag', 'featured'))
  .mustNot(new FilterBuilder().match('deleted', true))
  .build();
```

---

## Core Methods (13 Total)

### Collection Operations

| Method | Description |
|--------|-------------|
| `createCollection(name, vectorsConfig)` | Create collection with vector config |
| `getCollection(name)` | Get collection info |
| `listCollections()` | List all collections |
| `deleteCollection(name)` | Delete a collection |
| `collectionExists(name)` | Check if collection exists |

### Point Operations

| Method | Description |
|--------|-------------|
| `upsert(collection, points)` | Insert/update points |
| `search(collection, vector, options)` | Vector similarity search |
| `searchBatch(collection, vectors, options)` | Batch search |
| `retrieve(collection, ids, options)` | Get points by ID |
| `deletePoints(collection, ids)` | Delete points by ID |
| `deletePointsFilter(collection, filter)` | Delete by filter |

### Utility

| Method | Description |
|--------|-------------|
| `count(collection, options)` | Count points |
| `getHealth()` | Health check |
| `getClusterInfo()` | Cluster information |

---

## API Key Auth

```typescript
private getHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (this.apiKey) headers['api-key'] = this.apiKey;
  return headers;
}
```

---

## Test Pattern (16 Test Suites)

```typescript
describe('Qdrant SDK', () => {
  describe('createCollection', () => {
    it('should create collection with correct config', async () => { /* ... */ });
    it('should handle already exists error', async () => { /* ... */ });
    it('should handle network errors with retry', async () => { /* ... */ });
  });

  describe('search', () => {
    it('should search with vector and return results', async () => { /* ... */ });
    it('should apply limit and offset', async () => { /* ... */ });
    it('should apply filter conditions', async () => { /* ... */ });
    it('should handle empty results', async () => { /* ... */ });
  });

  describe('FilterBuilder', () => {
    it('should build must conditions', async () => { /* ... */ });
    it('should build must_not conditions', async () => { /* ... */ });
    it('should chain multiple condition types', async () => { /* ... */ });
  });

  // ... 16 total suites covering all methods
});
```

Use `nock` or `fetch` mocking for HTTP interception in tests.

---

## Export Pattern

```typescript
// index.ts
export { Qdrant, QdrantConfig } from './lib/qdrant/qdrant';
export { FilterBuilder } from './lib/qdrant/filter-builder';
```

---

## Key Differentiators (vs Raw REST)

| Aspect | Raw REST | This Pattern |
|--------|----------|--------------|
| Retry | Manual | Automatic (5x exponential) |
| Auth | Manual header | Built-in API key |
| Filters | Raw JSON | Chainable builder |
| Type safety | `any` | Full TypeScript types |
| Tests | Integration only | Unit + integration |

---

## Related Prompts

- `bounty-pat-write-access.md` — PAT scope limitations for upstream PRs
- `bounty-saturation-detection.md` — EdgeChains repo saturation data
- `external-bounty-clean-branch.md` — Clean branch preparation workflow
