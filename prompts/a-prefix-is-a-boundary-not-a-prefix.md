# A Prefix Is A Boundary, Not A Prefix

**Last verified: 2026-11-27** — `tiny-config` 0.4.4 (`980cfaa`). Five scenarios
run against the live tree and against `16cebb7` (0.4.3) in this container; each
one red on the old revision and green on the new. Suites: 137 passed / 14
skipped both sides.

A prompt for auditing any "read the environment with a prefix" API — `from_env`,
`os.environ` scanners, `EXTRA_*` settings, CI variable namespaces.

## The claim to test

> `from_env(prefix="APP")` reads *APP's* variables and nothing else.

It is almost always implemented as `key.startswith(prefix)`. That is a
**substring test pretending to be a namespace test**, and it fails in both
directions at once.

## What it actually does (measured, 0.4.3)

| env | 0.4.3 result | why |
|---|---|---|
| `COLTEST_DB__HOST=a`, `COLTEST2_DB__HOST=b` | `{'db': {'host': 'a'}, '2_db': {'host': 'b'}}` | `COLTEST2_...` starts with `COLTEST`, so a neighbour app's variable is absorbed as the key `2_db.host` |
| `COLTEST_SVC__PATH=/usr`, `COLTEST_SVC__path=/ci` | `{'svc': {'path': '/ci'}}` | both names flatten to the same dotted key; last writer wins |
| the same two, **created in the other order** | `{'svc': {'path': '/usr'}}` | the answer depends on `os.environ` iteration order |
| `COLTEST_A__B=2`, `COLTEST_A__B__C=1` | `TypeError: 'int' object does not support item assignment` | a value and a table claim the same node; the failure is a Python builtin, not a config error |
| `COLTEST_DB__=x` | `{'db': 'x'}` | a trailing separator silently becomes a leaf; the value has no field to land in |
| `COLTEST_USER__ID=1` | `{'user': {'id': True}}` | see below — the type is inferred by content |

Row 2 and row 3 are the expensive pair: **the same container produced different
settings on different boots**, and neither output looks wrong. There is no
error to search for.

## The rules

**Rule: the question is "does this name begin with the prefix, and is what
follows the separator" — so write both halves.** The boundary is the
*separator*, not the prefix. `key[:len(prefix)] == prefix` is necessary and not
sufficient; `body[:len(sep)] == sep or body[:1] == "_"` is the other half. An
implementation that checks only the first half is the bug above.

**Second rule: a prefix written with its trailing separator must mean the same
application.** `MYAPP_` and `MYAPP` are the same namespace written by two
people. Normalise the prefix (strip one trailing separator or lone `_`) before
comparing, or half your callers silently read nothing.

**Third rule: when two names reach one key, raise and name both.** Case-only
collisions are not a user error you can correct silently — on a case-insensitive
filesystem the two names are *the same file*, and a CI runner will inject
`SVC__PATH` while a shell injects `SVC__path`. Keep neither; report both, so
the reader knows which two variables to rename. Resolving by iteration order is
an answer that changes.

**Fourth rule: the duplicate check must be done on the sorted set.** `os.environ`
has no order contract. Collect `(key, parts, value)` for every variable first,
then make every collision decision on that list. Doing it during iteration is
how the same config has two answers.

**Fifth rule: a name whose value can never be read must raise.** `MYAPP_DB__`
(empty field), `MYAPP__` with a value (no key at all), and a leaf that is also a
prefix of a longer path all leave a value in the dict that no lookup returns.
Silence here is worse than a loud failure: the caller sees a key missing and
concludes the default applied.

**Sixth rule: do not infer a type from a one-character string.** `API_KEY=1`
became `True`. An API key, a tenant id, a port, and a feature flag all arrive as
one character. `"1"`/`"0"` are numbers; only the unambiguous words
(`true/false/yes/no/on/off`) are booleans; `get_bool`/`get_int` accept a
numeric string so no caller changes. Assert the **type** with an explicit
predicate (`type(v).__name__ == "int"`), never inside a formatted string: a
composite like `f"{type(v).__name__}:{v}"` produces a failure message that is
indistinguishable from a value change.

## The probe

```python
import os, tiny_config as t

def probe(env, prefix):
    old = dict(os.environ)
    os.environ.clear(); os.environ.update(env)
    try:    return repr(t.from_env(prefix=prefix))
    finally: os.environ.clear(); os.environ.update(old)

print(probe({"APP_DB__HOST": "a", "APP2_DB__HOST": "b"}, "APP"))
print(probe({"APP_SVC__PATH": "/usr", "APP_SVC__path": "/ci"}, "APP"))
print(probe({"APP_SVC__path": "/ci", "APP_SVC__PATH": "/usr"}, "APP"))  # reversed
```

Run the second and third and **compare them**. If they differ, the config is
read from a dict whose order you do not control.

## A correction worth carrying

The 0.4.4 changelog and code comment explain the slice comparison by claiming
that `"COLTEST_DB__HOST".startswith("COLTEST__")` returns `False` "in this
build". Measured here on CPython 3.12.15 it returns **`False`** — and so does
the slice, because the string genuinely does not begin with `COLTEST__`
(the 9th character is `D`). Both agree on every pair tried. The *real* defect is
`startswith(prefix)` **without** the separator, as table row 1 shows.

The slice is still the better spelling — it states the boundary directly and
has no search implementation to depend on — but it is not what fixed this bug,
and a claim that a builtin misbehaves must be paired with the literal it
returned. A comment that justifies a correct line with an unreproducible fact
sends the next reader hunting for a runtime bug that does not exist. See
`tools/probing-a-boundary-in-five-lines.md`.
