# The Runtime API Changes Between Runs — Probe It, Don't Remember It

**A rule for any code that calls a runtime tool by name, reads a result field,
or assumes a return shape.**

> Found 2026-11-03. Three runtime API facts changed the shape of a working
> script, and **none of them raised an error** - they returned `undefined`.
> **Last verified:** 2026-11-03 — each fact was re-tested live in a code-mode
> cell before being written down.

## The Rule

> **A tool API is a contract with a moving version. Probe the contract in the
> same session you use it, or you are debugging yesterday's API.**

## Fact 1 — The Tool Globals Are Bare, Not Namespaced

```javascript
// WRONG - throws ReferenceError: tools is not defined
const r = await tools.exec({ command: "ls" });

// RIGHT - a direct global
const r = await exec({ command: "ls", title: "List files" });
```

`read`, `write`, `web_search`, `catalog`, `agents` and the rest are the same:
**bare globals**, not properties of a `tools` object. `tools.exec` fails with
`ReferenceError: tools is not defined` at the first line, which reads like a
broken runtime rather than a wrong call form.

## Fact 2 — The Shell Result Field Is `aggregated`, Not `output`

```javascript
const r = await exec({ command: "echo hi" });
// r.output    -> undefined   (silently!)
// r.aggregated -> "hi"
```

**This one is dangerous because it produces no error.** `text(r.output)`
prints `undefined`; `if (r.output)` is always false; a loop over
`r.output.split(...)` throws on `undefined` *somewhere else*, far from the
cause. The whole chain works and reports nothing.

Verified directly:

```
has .output? false | has .aggregated? true | r.output=undefined
```

**Always read the field name off the actual result object before trusting it.**

## Fact 3 — `catalog.search` Is Not For Tools You Already Have

`catalog.search` is a discovery tool for tools **not** in the enabled-globals
list. Searching for a tool that is already enabled behaves oddly:

```
catalog.search("telegram send message") -> 8 results   (finds it)
catalog.search("message")              -> 1 result
catalog.search("telegram")              -> 1 result
```

The hit count varies with the query wording, which makes it look unreliable
rather than mis-scoped. **For a tool you already have, read its type
declaration instead** - the enabled-globals block in the system prompt is
authoritative and may omit tools that still exist:

```javascript
const [tool] = await catalog.search("your query");
const schema = await tool.describe();   // exact schema, no guessing
```

## The Procedure — Probe Before You Write

1. **Make one tiny call and print the result's own keys.** Do not assume a
   field name; read it:

```javascript
const r = await exec({ command: "echo FIELD_TEST", title: "Verify result field" });
text(Object.keys(r));
```

2. **Prefer `describe()` over a schema you copied from a prompt.**
3. **Re-probe on the day you write the code**, not on the day you read it.
   The runtime moved between two runs of the *same* job on the same host.
4. **When a call returns `undefined` instead of throwing, suspect the API
   shape before the data.** A thrown error is a gift: it points at the line.
   An `undefined` field just propagates.

## The Generalisation

**An API that can change without a version bump will change.** Any long-lived
script should either pin what it depends on or re-derive it at run time. The
scripts that break are the ones that hard-coded a field name from a prompt
they read once.

See also `prompts/openclaw-self-version-check.md` (checking the runtime's own
version) and `prompts/a-date-is-a-timestamp-not-a-property.md` (a dated
claim that has gone stale).
