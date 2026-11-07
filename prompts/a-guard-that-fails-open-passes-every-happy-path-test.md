# A Guard That Fails Open Passes Every Happy-Path Test

**A check whose absence is silent cannot be tested by a suite that only walks
the success path.**

> Found 2026-11-07 in `tiny-mcp-client`, shipped the same day.
> **Last verified:** 2026-11-07 (12:00 EST) — fresh clone of `main`,
> `pytest -q` -> **40 passed**; the mutation run (guard stubbed out) gave
> **5 failed, 35 passed**; restoring the guard returned **40 passed**.

## The rule

> **Deleting the guard must break a test. If it does not, you tested the code
> the guard is *in front of*, not the guard.**

A capability check is a rejection: it does nothing on the happy path, which is
the only path a normal suite walks. So it is green when present, green when
absent, and green when wrong.

## What happened

`tiny-mcp-client` parsed the `initialize` result and then ignored its
`capabilities` object. Per the MCP spec, a server that omits a capability is
stating that it does not implement it — but the client sent `tools/list`
anyway.

The miss did not look like a client defect. It surfaced as:

```
MCPError: [Errno -32601] Method not found
```

a transport-shaped error for a contract-shaped defect, arriving at call time
instead of at `initialize` time.

The fix is three members:

```python
class MCPCapabilityError(MCPError):
    """Server did not advertise a capability the call needs."""
    def __init__(self, capability, method, message=None):
        self.capability = capability
        self.method = method
        super().__init__(code=-32601, message=message or f"...")
```

plus `capabilities`, `supports(name)` and `_require(capability, method)` wired
into `list_tools()` and `call_tool()`. Nothing on that list can be observed by
a passing test.

## How it was proved

| step | result |
|---|---|
| suite before the guard | 33 passed |
| suite with the guard | **40 passed** |
| `_require()` replaced by the old bare branch | **5 failed, 35 passed** |
| guard restored | **40 passed** |

The middle row is the whole argument. A guard you have not watched fail is a
comment.

**Include a positive control.** One of the seven new tests asserts that a
server which *does* advertise `tools` succeeds. Without it, the guard passes
by blocking everything, and every rejection test is satisfied by a client that
refuses to work.

**Malformed input is absent input.** `"capabilities": "tools"` — a string where
an object belongs — must mean *advertised nothing*, not `TypeError` raised from
inside a property. Both absence and garbage mean "cannot use this", and both
deserve the named error.

**A new error belongs inside the existing hierarchy.** `MCPCapabilityError`
subclasses `MCPError`, so every `except MCPError:` at every call site keeps
working. A sibling class turns a recoverable capability miss into an uncaught
crash in exactly the handler written to survive it.

## The general form

| guard kind | how it fails silently | the test that catches it |
|---|---|---|
| capability / feature check | method simply works when the guard is gone | stub the guard out, assert rejection |
| authz branch | default-allow when the branch is deleted | delete the branch, watch a denial test fail |
| schema `required` | extra key ignored | remove each required field, assert rejection |
| redaction | returns input unchanged | spy on the output for the literal |

The measurement is the same in all four: **remove it and watch something go
red.** If nothing goes red, nothing was guarded.

## Still open

The same rule applies on the server side, where it is not yet implemented:
`tiny-mcp-server` answers `tools/list` and `tools/call` unconditionally and
returns `-32601 method not found` for a capability its `initialize` never
advertised. Measured 2026-11-07 against a fresh clone (`16 passed`).
