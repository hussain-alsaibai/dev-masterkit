# Probing Both Paths of a Default

**Last verified: 2026-11-25** — this probe found the `tiny-cli` 1.3.3 defect on
a tree whose 143 tests were green, and confirmed the `tiny-router` 0.9.5 CORS
fix in all four directions before any test was written.

## The rule

`probing-a-boundary-in-five-lines.md` probes the **input** domain. This is the
other axis: probe the **path** the value arrived by. Any default has at least
two paths — **supplied** and **omitted** — and a suite that always supplies the
value tests exactly one of them.

## Path 1: supplied vs omitted

Call the *same* callable twice and compare the types, not the values.

```python
import io, contextlib, json
import tiny_cli as tc

def build():
    app = tc.App("t")
    @app.command("top")
    def top(limit: int = tc.option("--limit", default=10)):
        print(json.dumps({"limit": limit, "type": type(limit).__name__}))
    return app

for argv in (["top"], ["top", "--limit", "5"]):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        build().run(argv=argv)
    print(argv, "->", buf.getvalue().strip())
```

Before 1.3.3:

```
['top']           -> {"limit": 10,   "type": "int"}
['top', '--limit', '5'] -> {"limit": "5", "type": "str"}   # same parameter, two types
```

After:

```
['top']           -> {"limit": 10,  "type": "int"}
['top', '--limit', '5'] -> {"limit": 5, "type": "int"}
```

Printing `type(...).__name__` is the whole trick. `10 == 10` and `"10" == 10`
are indistinguishable if you only look at the value in a loose comparison;
printing the type makes the divergence impossible to miss.

## Path 2: explicit vs implied (and who enforces the rule)

For a validation, probe the omission that resolves to the permissive value, and
probe **the party that actually enforces it**. Here the enforcement was the
browser's, not the library's:

```python
import tiny_router as tr

class R:
    def __init__(self, m, h): self.method, self.headers = m, h
def p(_r): return tr.Response("ok")

# 1. the dangerous combination must be refused at construction time
for kw in ({"allow_credentials": True},
           {"allow_origins": ["*"], "allow_credentials": True}):
    try:
        tr.cors(**kw); print("NOT REFUSED", kw)
    except ValueError as e:
        print("REFUSED:", str(e)[:110])

mw = tr.cors(allow_origins=["https://app.example"], allow_credentials=True)
# 2. its own origin still gets the grant
print(mw(R("GET", {"origin": "https://app.example"}), p).headers)
# 3. a foreign origin must get NOTHING -- not a refusal of the request, an
#    ABSENCE of the grant headers
print(mw(R("GET", {"origin": "https://evil.example"}), p).headers)
# 4. the non-credentialed wildcard must still be legal
print(tr.cors(allow_origins=["*"])(R("GET", {"origin": "https://x.example"}), p).headers)
```

Measured 2026-11-25 on `1c64aee`:

| probe | result |
|---|---|
| `cors(allow_credentials=True)` | `ValueError` naming `allow_origins` and the remedy |
| `cors(allow_origins=["*"], allow_credentials=True)` | `ValueError` |
| own origin, credentials on | `Allow-Origin: https://app.example`, `Allow-Credentials: true` |
| foreign origin, credentials on | both headers **absent** |
| `cors(allow_origins=["*"])`, no credentials | reflected origin, no `Allow-Credentials` |

## Why four directions, not two

A security fix has two ways to be wrong. **Too permissive** is the bug you
fixed; **too strict** silently breaks the legitimate deployment, and it does so
in a way the original tests would never have caught because they never covered
the safe configuration at all. Row 5 is the one that keeps the fix shippable:
a non-credentialed wildcard is legal and must stay legal.

## Checklist

1. Two calls, same callable, value supplied and omitted. Print the type.
2. One call per sentinel/default path — the omitted argument, the empty
   argument, the wildcard.
3. **Name who enforces the rule.** If the answer is the browser, a client, or a
   downstream service, probe what the library emits, not what the failure looks
   like.
4. Probe the *legitimate* configuration too, and assert it still works.
5. Only then write the test — and confirm it is red on the previous release.

## Related

- `prompts/name-who-enforces-it-and-which-path.md`
- `tools/probing-a-boundary-in-five-lines.md`
- `tools/probing-a-one-path-fix.md`
