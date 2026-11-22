# tiny-prompt-cache — Zero-Dependency Prompt Prefix Cache for LLM Calls

**Repo:** github.com/hussain-alsaibai/tiny-prompt-cache
**Install:** `pip install git+https://github.com/hussain-alsaibai/tiny-prompt-cache.git` (not on PyPI — copy `prompt_cache.py` instead if you prefer vendoring)
**Last verified:** 2026-11-22 (v0.1.1, `d51e093`; suite **66 passed** in this container)

Caches LLM responses keyed by the **prompt string**, with an optional semantic
layer (`semantic_threshold` + `embedding_fn`), TTL, bounded LRU eviction,
`@cached` decorator, thread-safe. Keying is the caller's job — build the key
from the system prompt plus the prefix you want to reuse (see below).

## Why prefix caching, not response caching

Two calls with the same system prompt and a different question share almost all
of their input tokens. A whole-response cache misses both. A prefix cache hits
the *prefix*, which is where the bill is. Check the prefix mode against your
traffic before trusting a hit rate:

There is no built-in prefix mode; the key is whatever you pass. The three
shapes that worked in practice:

| key shape | hits when |
|---|---|
| `system` alone | the system prompt is stable across turns — best hit rate, coarsest |
| `system + first N words of user` | conversational turns that restate context |
| `system + fixed header block` | templated prompts |

## v0.1.1 — what changed (2026-11-22)

`get_or_call` ran `len(response)` **before** storing. A `None` response from the
backend raised `TypeError` on the **first** call — the cache could not cache a
value the model is free to return. Its hit test was also `is not None`, so a
cached `None` re-ran the call.

Fixed with:

- a private `_MISSING` sentinel, used as the default in `_get` — so "no entry"
  and "an entry whose value is `None`" are distinguishable
- a public `has(prompt) -> bool` for callers that only want presence
- the token estimate computed **only for `str`** (`isinstance(response, str)`),
  so `len(None)` can no longer raise on the first call

Executed against `d51e093`:

```
>>> c.get_or_call(p, lambda: None)
None
>>> c.has(p)
True
>>> c.get_or_call(p, lambda: "x")
None            # the cached None is a hit; the factory did not run
```

Verification recorded:

```
repos/tiny-prompt-cache @ d51e093   ->  66 passed
0.1.0 + 0.1.1's tests                ->  4 failed (documented in the 0.1.1 commit)
```

Distribution detail worth repeating: **v2 existed only on
`feature/prompt-cache-v2`** at the time the fix was written. `origin/main` had no
v2 module at all, so the fix was merged to `main` (`d51e093`) — without that,
anyone installing the default branch got the broken v1-era code with no v2
module. `git ls-tree origin/main <path>` is the one-command check.

## Usage

```python
from prompt_cache import PromptCache

cache = PromptCache(ttl_seconds=3600, max_size=1000)

def key(system, user, words=8):
    return system + "\x00" + " ".join(user.split()[:words])

def ask(system, user):
    k = key(system, user)
    return cache.get_or_call(k, lambda: client.chat(system=system, user=user))
```

When the backend can return `None`, `get_or_call` is already correct — it
returns the cached `None` rather than re-calling. If you branch on the return
value yourself, test presence, not truthiness:

```python
if cache.has(k):                 # v0.1.1
    return cache.get(k)
```

Constructor keywords are `max_size`, `ttl_seconds`, `semantic_threshold`,
`embedding_fn`, `cost_per_1k_tokens` — verified by signature at `d51e093`.

## When NOT to use

- Multiple processes sharing one cache directory without a lock — the file
  storage is atomic per write, not transactional across readers
- Prompts whose prefix changes every turn (a timestamp in the system prompt is
  the classic own-goal): the hit rate goes to zero and the cache is pure overhead
- You need semantic matching — this is an exact prefix cache. See the semantic
  cache guide for that layer.

## Related

- `prompts/a-cache-that-cannot-store-none-is-not-a-fix.md` — the rule this
  release carries, and its two siblings in one month
- `tools/probing-a-one-path-fix.md` — how the sync/async and v1/v2 pairs were
  found and proven
- `tools/tiny-semantic-cache-guide.md` — the semantic layer, if exact prompts
  are too strict for your traffic
