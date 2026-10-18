# tiny-jsonpath v0.1.0 — RFC 9535 (JSONPath 1.0) Parser & Evaluator

**Last verified:** 2026-10-18
**Repo:** https://github.com/hussain-alsaibai/tiny-jsonpath
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** ~830 (lib) + ~600 (tests) • **Tests:** 49/49

## What it solves

JSONPath is the IETF-standard way to query JSON (RFC 9535, 2024). Most existing
Python implementations either pull in a non-stdlib JSON library, ship a multi-thousand-line
parser, or only support the older Stefan Goessner syntax. `tiny-jsonpath` is the
~830-LOC stdlib-only pure-Python RFC 9535 parser. Single file, drop-in import, runs
anywhere CPython runs, and the AST nodes are inspectable from your own tools.

## Public API

- `find(path: str, doc: Any) -> list[Any]` — return all matches (empty list when nothing matches)
- `find_one(path: str, doc: Any, default=None) -> Any` — return first match or `default`
- `JSONPathError` — parse / evaluation errors with `position` attribute and caret-pointed excerpt
- AST nodes: `Root`, `Name`, `Index`, `Slice`, `Wildcard`, `Recursive`, `Union`, `Filter`, `Path`

## Supported (RFC 9535 subset)

- **Root** `$`
- **Member access** `.name` and `['name']`
- **Array index** `[i]`, negative indices
- **Array slice** `[start:end:step]` — all 8 forms (`[a:b:c]`, `[:b:c]`, `[a::c]`, `[a:b]`, `[:b]`, `[a:]`, `[:]`, `[::c]`)
- **Wildcard** `[*]` and `.*`
- **Recursive descent** `..name`
- **Union** `[a, b, c]`
- **Filter expressions** `[?(@.x > 5)]` with `== / != / < / <= / > / >= / =~`, `&&`, `||`, optional parens, literals, paths
- `find_one()` with default value

Out of scope (deliberately):
- Script expressions (Goessner extension)
- Function calls inside filters (`length()`, `match()`, etc.)

## Quick start

```python
from tiny_jsonpath import find, find_one

doc = {
    "store": {
        "book": [
            {"title": "Moby Dick",       "price": 8.99,  "category": "fiction"},
            {"title": "Sword of Honour", "price": 12.99, "category": "fiction"},
        ],
    },
}

find("$.store.book[*].title", doc)
# ['Moby Dick', 'Sword of Honour']

find_one("$.store.book[?(@.price < 10)].title", doc)
# 'Moby Dick'

find("$..price", doc)
# [8.99, 12.99]   (recursive descent)
```

## Errors

All parse / evaluation errors raise `JSONPathError` with a `position` attribute and a
one-line caret-pointed excerpt:

```python
from tiny_jsonpath import find, JSONPathError
try:
    find("$.foo[bar", {})
except JSONPathError as e:
    print(e)            # Unexpected character in union (line 1, col 7)
                        # $.foo[bar
                        #       ^
```

## Pairing with tiny-input-sanitize

JSONPath queries against untrusted input are themselves an attack surface: a hostile
query like `$..[*]` recursively scans every document node and can OOM the caller.
`tiny-input-sanitize` v0.1.0 ships a `jsonpath` context that validates queries against
an allowlist of selectors before they're passed to `tiny-jsonpath.find()`. Pattern:

```python
from tiny_input_sanitize import sanitize_text
from tiny_jsonpath import find

def safe_find(query: str, doc, *, max_length=512):
    cleaned = sanitize_text(query, context="jsonpath",
                            allow="$[]:*?.,'", max_length=max_length)
    if not cleaned.is_safe(threshold=0.95):
        raise ValueError("untrusted jsonpath query failed allowlist")
    return find(cleaned.value, doc)
```

## When to use

- Agent tool surfaces that need to slice JSON config files, API responses, or stored
  documents by a user-supplied query
- Internal config validators that want RFC-compliant paths over ad-hoc dotted strings
- Anywhere the Goessner syntax (`$.store.book[0].title`) is hand-rolled today and the
  team would benefit from filters, slicing, and recursive descent

## When NOT to use

- High-throughput JSON querying of very large documents — this is a stdlib parser, not
  Cython/C. For >10k docs/sec, use `jsonpath-ng` or `python-jsonpath-rfc9535` (which is
  also RFC-compliant but faster via caching).
- Expression evaluation needs (`$..book[?(@.price < $.max)]` with cross-doc comparisons)
  — out of scope for this subset.
- You need the legacy Goessner syntax (`$.store.book[(@.length-1)]` script expressions).
  Use `jsonpath-ng` for that.

## Test highlights (49/49)

Root + name + bracket member, all 8 slice forms + step edge cases (zero, overshoot,
negative), wildcard + recursive descent, unions of index + slice + name, filter
expressions with all 7 operators + `&&`/`||` + parens, error positions on bad input,
`find_one` default behavior, deeply nested documents, mixed-type arrays.

## Sidecar-friendly

Single-file library. Drop `tiny_jsonpath.py` next to your code and `import tiny_jsonpath`
without touching your requirements file. Pairs naturally with `tiny-input-sanitize`
(JSONPath context) for safe querying of untrusted queries.