# Probing a Boundary in Five Lines

**Last verified: 2026-11-24** — the probe below found the `tiny-log` 0.8.3 unit
bug in under a minute on a tree whose 140-test suite was green, and confirmed
the `tiny-validator` 0.7.4 nullable fix before any test was written.

## The rule

**Before writing a test, before reading the diff, run the function at the
boundary in a REPL.** One line per boundary input.

```python
import tiny_log as t
for v in (1023.9999, 1048575.99, 0, -1, float("nan"), float("inf")):
    print(v, "->", t.bytes_human(v))
```

Output on the broken release:

```
1023.9999     -> 1024.0 B      # number equals the next unit's base; label says B
1048575.99    -> 1024.0 KB
0             -> 0 B
-1            -> -1 B
nan           -> NaN B
inf           -> OverflowError # raised INSIDE a logging call
```

Out of one probe: a 1024x error, a contradiction between value and unit, and an
exception from a formatter that must never raise.

## Which inputs to try, in this order

1. **Just below a change boundary** — `1024 - ε`, `99 - ε` for a two-digit
   format, `rate * 0.999`. This is where "computed separately" bugs live.
2. **The sentinels** — `0`, `-0.0`, `None`, `""`, `inf`, `-inf`, `NaN`.
3. **The empty and the one-element collection** — `[]`, `[None]`.
4. **The round trip** — `parse(render(x)) == x`, `import(export(s))` valid.
5. **The type variants** — `True` (an int), `1` vs `"1"`, enum vs its name
   (`logging.DEBUG` → `"10"` → lookup by `"DEBUG"` fails).

## Why five lines beat a suite rerun

The suite proves the cases it names. The probe names the case the suite cannot
guess — the one where two halves of the same fact disagree. It costs seconds,
and it produces a **receipt** (the before/after output) that goes straight into
the commit message.

## Anti-patterns

- Probing after the fix, to "confirm" — that confirms nothing; run it on the
  broken tag first and keep the output.
- Probing with a sample from the middle of the domain (`1536`, `2.5 MB`) —
  every one of those passes on the broken code.
- Trusting a green suite as evidence the boundary is covered. Grep the tests
  for the literal boundary value; if it is absent, it is not covered.

---

## The membership case: a prefix is a boundary (added 2026-11-27)

**Last verified: 2026-11-27** — `tiny-config` 0.4.4 (`980cfaa`). Five scenarios
run against the live tree and against `16cebb7` (0.4.3) in this container; each
one changes classification between the trees.

The 2026-11-24 rows above probe a **value** at a boundary. The same probe shape
audits a **name** at a boundary — any API that decides membership by string
(`prefix=`, `namespace=`, `root=`) — and there the boundary is usually the
*separator*, not the prefix.

### The five lines

```python
def probe(env, prefix):
    old = dict(os.environ)
    os.environ.clear(); os.environ.update(env)
    try:     return repr(t.from_env(prefix=prefix))
    finally: os.environ.clear(); os.environ.update(old)
```

Everything that matters is `env`: a dict small enough to verify by eye. The
`finally` is most of the code, because `from_env` reads the process's real
environment — a probe that forgets to restore it corrupts every later test in
the run, and leaves the *next* probe's result depending on this one.

### The table that does the work

Build these five rows for **any** prefix matcher. Each kills a different wrong
implementation; the order is cheapest first.

| # | input | names | what it proves |
|---|---|---|---|
| 1 | `P_A`, `P2_A` | one real, one neighbour | membership is a **boundary**, not a substring |
| 2 | `P_X`, `P_x` | two names, one key | a collision must be reported, not resolved |
| 3 | row 2, dict created **in reverse order** | same | the answer does not depend on iteration order |
| 4 | `P_A__B` **and** `P_A__B__C` | a leaf that is also a branch | the error names the variables, not a builtin |
| 5 | `P_A__` (trailing separator) | a leaf with no field | an unreadable value raises instead of hiding |

Measured on `16cebb7` (0.4.3) versus `980cfaa` (0.4.4):

```
# 0.4.3
1  {'db': {'host': 'a'}, '2_db': {'host': 'b'}}   # neighbour absorbed
2  {'svc': {'path': '/ci'}}                       # last writer wins
3  {'svc': {'path': '/usr'}}                      # ...the other writer
4  TypeError: 'int' object does not support item assignment
5  {'db': 'x'}                                    # value with nowhere to land
# 0.4.4
1  {'db': {'host': 'a'}}
2  ConfigError: 'COLTEST_SVC__PATH' and 'COLTEST_SVC__path' both set 'svc.path'
3  (same error)
4  ConfigError: 'COLTEST_A__B__C' needs 'b' to be a table, but it is already set to 2
5  ConfigError: 'COLTEST_DB__' would produce the key '', which is not a name
```

**Row 3 is the one people skip, and it is the only row that catches "last
writer wins".** Rows 2 and 3 return *different plausible configs*; neither looks
wrong, and there is no error to search for. Run both in one script and diff the
outputs — reversing a `dict` literal is a real reversal, since `os.environ` is
populated in insertion order.

### Compare the two trees, not the two runs

A row that prints `OK` on the broken tree **and** the fixed tree is a row that
tests the probe. Export the old file and run the identical table through it:

```bash
python proof_0_4_5.py --against 16cebb7
```

Every row must change classification. If five rows are green on both, the probe
is wrong before the code is.

### The trap this shape was built for

A boundary bug and an ordering bug look **identical in a single run**. Both
print a complete, plausible config. The only separator is reversing the
insertion order — which is also why "it worked when I tried it" is not evidence
about a dict-ordered input.

See `prompts/a-prefix-is-a-boundary-not-a-prefix.md` for the six rules this
table checks, including the one-place where the upstream changelog's explanation
of its own fix does not reproduce.
