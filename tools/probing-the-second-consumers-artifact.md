# Probing a second consumer: the four calls that catch a lossy export and a lossy write

**Last verified: 2026-11-26 17:00Z** — every command and output below was run
in this container against freshly cloned upstream trees:

```
snapdb        0.18.5  288e97e   /home/node/venvs/mx-3.12/bin/python -m pytest -q  -> 277 passed, 22 skipped
tiny-validator 0.7.5  161f444   /home/node/venvs/mx-3.12/bin/python -m pytest -q  -> 246 passed,  4 skipped
```

`python3 -m pytest` in this container answers `No module named pytest`. A
verification line without the interpreter is indistinguishable from a skipped
suite.

## Why four calls

Each of these libraries was **correct in memory and wrong at the boundary**.
Every existing test asserted the in-memory object. These four assert the artifact
a second system consumes.

| # | library | the call | catches |
|---|---|---|---|
| 1 | validator | `to_json_schema(from_json_schema(doc))` | a constraint the import enforced but the export forgot |
| 2 | validator | `validate(bad)` on the **exported** document | the mirror: a contract narrower or wider than the validator |
| 3 | store | `update(id, {one_field})` then `get(id)` | a write API spelled as a patch but implemented as a rewrite |
| 4 | store | `update(nonexistent_id, {...})` | a write that invents a row instead of raising |

## 1 + 2 — tiny-validator 0.7.5

```bash
cd /tmp && git clone -q --depth 5 https://github.com/hussain-alsaibai/tiny-validator.git tv075
cd tv075 && /home/node/venvs/mx-3.12/bin/python - <<'PY'
import tiny_validator as tv
doc = {"type":"object","properties":{"role":{"type":"string","enum":["admin","user"]}}}
s = tv.from_json_schema(doc)
print("rejects root:", s.validate({"role":"root"}))
print("export:", tv.to_json_schema(s))
PY
```

Actual output **after** the 0.7.5 fix:

```
rejects root: [{'path': 'role', 'message': "value must be one of ['admin', 'user']"}]
export: {'type': 'object',
         'properties': {'role': {'type': 'string', 'enum': ['admin', 'user']}},
         'additionalProperties': False}
```

On 0.7.4 the first line printed **identically** and the export had
`{'properties': {'role': {'type': 'string'}}}` — no `enum`. **The reject call
alone cannot detect this**; you must read the export. That is the whole point:
the test that "proves enum works" is green on the broken release.

## 3 + 4 — snapdb 0.18.5

`DocumentStore` is not exported from the package root; import it from its module
and give it a **path** (it is a file-backed store):

```bash
cd /tmp && git clone -q --depth 5 https://github.com/hussain-alsaibai/snapdb.git snapdb-185
cd snapdb-185 && /home/node/venvs/mx-3.12/bin/python - <<'PY'
import tempfile, os
from snapdb.document_store import DocumentStore
s = DocumentStore(os.path.join(tempfile.mkdtemp(), "t.snap"))
s.insert({"name":"alice","age":30,"role":"admin"})
s.update(0, {"age":31})
print("after partial update:", s.get(0))
try:
    s.update(99, {"age":1}); print("update(missing) DID NOT RAISE")
except Exception as e:
    print("update(missing) ->", type(e).__name__, e)
s.replace(0, {"name":"bob","age":40,"role":"user"})
print("after replace:", s.get(0))
PY
```

Actual output on 0.18.5:

```
after partial update: {'name': 'alice', 'age': 31, 'role': 'admin'}
update(missing) -> IndexError no document at index 99
after replace: {'name': 'bob', 'age': 40, 'role': 'user'}
```

On 0.18.4 the same script printed `after partial update: {'age': 31}` and
`update(99, …)` **created a placeholder row with no error**.

## The trap in copying this procedure

- `from snapdb import DocumentStore` fails on every release — use
  `snapdb.document_store`. Import the name the *library* exports, then check
  `dir()` rather than assuming the README's spelling.
- `DocumentStore()` without `path` is a `TypeError`. A probe that fails on setup
  proves nothing about the library; read the traceback before recording a result.
- The `tiny-validator` export also emits `additionalProperties: False`. Comparing
  whole dicts with `==` flags it as drift even when the library is right — compare
  **the field the defect was about**.

## Rule this guide encodes

**A probe must read the second consumer's artifact, not the first system's
response.** `s.validate(bad)` answers "does it reject"; it cannot answer "does it
still say so". Those are different assertions about different objects and only
one of them is the published contract.
