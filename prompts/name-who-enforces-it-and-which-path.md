# Name Who Enforces It, And Which Path It Applies To

**Last verified: 2026-11-25** — used to find and fix two defects in one day
(`tiny-router` 0.9.5 `1c64aee`, `tiny-cli` 1.3.3 `11c9539`). Both fixes were
probed against the shipped source in this container, with the suite green
before and after.

## When to use it

When a rule, guard, or validation exists in code, do not ask "is it
implemented?" — ask two questions instead:

1. **Who enforces it?** The library, or somebody downstream that happens to
   catch it?
2. **Which code path does it cover?** The explicit form, or every form?

A rule that is delegated downstream is **not enforced**, and a guard that
covers one path is a guard that covers the path the author was thinking about.

## The two failures this finds

### Declared vs enforced (and client vs server)

`tiny-router` 0.9.5: `cors(allow_credentials=True)` defaulted
`allow_origins=["*"]` and then **reflected the caller's `Origin`** back with
`Access-Control-Allow-Credentials: true`. Reflecting is *worse* than shipping
`"*"`, because `"*"` is rejected by the browser while a reflected origin is a
valid credentialed grant — any site could read authenticated responses.

The library "did not enforce" the Fetch rule that a wildcard origin cannot
carry credentials, because it never had to: browsers enforce it by withholding
the response. That is why the config looked fine in review and failed nothing.
**A library that delegates an illegal combination to the browser has not
validated it — and the failure it delegates is silent.**

Fix: `ValueError` at construction time, naming the remedy. Both directions
probed: dangerous combos refused; a specific origin still echoes and still
grants; a foreign origin gets no grant; a plain non-credentialed wildcard
remains legal.

### Supplied vs omitted

`tiny-cli` 1.3.3: `option()`/`argument()` declared `type: type = str`, so an
omitted `type=` meant `str` rather than "infer it". One parameter, two types,
chosen by the user's command line:

```
def top(limit: int = option("--limit", default=10)): ...
  top              -> limit == 10    (int, from the default)
  top --limit 5    -> limit == "5"   (str, from argv)
```

The same root cause made `choices=[1,2,3]` reject its own valid values, because
argparse compared the raw string against ints.

**Why it survived 143 green tests:** every existing test wrote `type=int`
explicitly — the single spelling that could not fail. A green suite proves the
cases it names, and it naturally names the surface's centre.

## Procedure

For every rule or default in the module under audit:

1. **Write the sentence "X is enforced by …"** and fill in the blank. If the
   answer is a browser, a caller, a downstream service, or a test, the library
   does not enforce it.
2. **Enumerate the paths**: supplied vs omitted, explicit vs implied, one
   value vs many, first request vs subsequent, preflight vs simple request.
3. **Probe the path the tests do not write.** For a default, that is the call
   site with the argument missing. For a validation, it is the omission that
   resolves to the permissive value.
4. **Fix at construction/parse time, not at use time**, and put the remedy in
   the error message.
5. **Add a test per path**, and confirm it is red on the previous release.

## Why it beats reading the code

Both defects read as correct. `allow_origins=["*"]` with credentials is a
plausible line, and `type: type = str` is a plausible default; each is only
wrong when you ask *who enforces this* and *which path reaches it*. The audit
is two questions per rule and it does not need a bug name.

## Related

- `prompts/two-computed-separately-things-must-agree.md` — the sibling shape
  (two computations that should agree, rather than one rule with two readers)
- `prompts/nullable-is-a-field-fact-not-a-missing-value.md` — absence vs null,
  the supplied-vs-omitted shape at the schema layer
- `tools/probing-a-boundary-in-five-lines.md`
