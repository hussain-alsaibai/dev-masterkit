# tiny-skill-loader Guide

> Runtime plugin / extension loader for AI agents. Discover, validate, mount, and call skills from a directory of single-file Python modules. ~275 LOC, 26 tests, stdlib-only.

**Repo:** `github.com/hussain-alsaibai/tiny-skill-loader`
**Version:** 0.1.0 (2026-10-10)
**Author:** OpenClaw (autonomous cron, daily-bounty-workflow context)
**Status:** ✅ Initial release — 26/26 tests passing. Zero runtime deps. Backward-compat with legacy `register(reg)` signatures.

---

## What is it?

`tiny-skill-loader` is a single-file Python library (~275 LOC) that turns a directory of `*.py` files into a registry of named tool calls the agent can route to at runtime.

It is the plugin layer for the 2026 Q4 "agent is a stack" pattern. See the [Developer Tools Landscape 2026-10-10](../../dev-reports/2026-10-10-developer-tool-trends.md) report (Pattern 3: "the manifest pattern") for the cross-ecosystem context.

## Why does it exist?

AI agents grow by accumulating *skills*: one module that scrapes Jira, another that summarizes a URL, a third that calls your internal billing API. After a year you have 30 of them. Now you need a loader that:

- Discovers them by file/directory glob
- Validates a manifest (`name`, `version`, `description`, `tags`, `requires`)
- Calls each module's `register(registry, manifest)` to wire tools into the agent
- Lets the agent's tool-call layer route by name: `reg.call_tool("jira.search", query="...")`
- Surfaces what got loaded (`reg.list_skills()`, `reg.list_tools()`)

`tiny-skill-loader` is that loader, in one file, ~275 LOC. No `importlib.metadata`, no entry-points, no setup.py.

## Usage

### A skill file

```python
# skills/jira.py
MANIFEST = {
    "name": "jira",
    "version": "0.1.0",
    "description": "Jira issue search and update",
    "author": "you@example.com",
    "tags": ["pm", "atlassian"],
    "requires": ["tiny-llm>=0.5"],
}

def register(reg, manifest):
    @reg.tool("jira.search")
    def search(query: str, limit: int = 10):
        return _call_jira("/search", {"q": query, "limit": limit})

    @reg.tool("jira.update_status")
    def update_status(issue: str, status: str):
        return _call_jira("/issue/" + issue + "/transitions", {"to": status})

    @reg.hook("agent.shutdown")
    def on_shutdown():
        _flush_jira_cache()
```

### Loading skills

```python
from tiny_skill_loader import discover_skills, SkillRegistry

reg = SkillRegistry()
for skill in discover_skills(["./skills/"]):
    reg.register_skill(skill)

print(reg.list_tools())
# ['jira.jira.search', 'jira.jira.update_status']

result = reg.call_tool("jira.search", query="open bugs", limit=5)
```

## Manifest

A `MANIFEST` dict must define:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | str | yes | Unique skill identifier (no slashes/spaces) |
| `version` | str | yes | Semver string |
| `description` | str | yes | One-line summary |
| `author` | str | no | Author/email |
| `tags` | list | no | Free-form search tags |
| `requires` | list | no | Other skill/package names |

The `register(reg, manifest)` function is optional. If present, it should call `reg.tool(name, fn)` or use the `@reg.tool("name")` decorator.

## API Reference

### Loaders

- `load_skill_from_file(path)` — load a single `.py` file
- `load_skill_from_dir(directory)` — load every non-underscore `.py` in a dir
- `discover_skills(paths, recursive=True)` — mixed list of files/dirs

### `SkillRegistry`

- `reg.register_skill(skill, overwrite=False)` — add a loaded skill
- `reg.unregister(name)` / `reg.get(name)`
- `reg.call_tool(name, *args, **kwargs)` — route by tool name (any skill)
- `reg.fire_hook(name, *args, **kwargs)` — call hook on every skill that has it
- `reg.list_skills()` / `reg.list_tools()`
- `@reg.tool("name")` — decorator; mounts a function as a callable tool
- `@reg.hook("name")` — decorator; mounts a function as a lifecycle hook

### Exceptions

- `SkillLoadError(message)` — manifest invalid, duplicate tool, file syntax error, etc.

## Backward compatibility

The loader accepts two legacy `register` signatures:

```python
# New: 2-arg form
def register(reg, manifest): ...

# Legacy: 1-arg form (manifest still discovered from module-level MANIFEST)
def register(reg): ...

# New: explicit manifest-only mode
def register(reg, manifest_only=True): ...
```

This makes it safe to mix new skills and old skills in the same directory.

## Cross-Repo Interop

`tiny-skill-loader` is part of the **OpenClaw developer tools ecosystem**:

- **tiny-tool-result** — every `call_tool` return value is wrapped in a `ToolResult` envelope
- **tiny-agent-scope** — `reg.list_tools()` is the input to `scope.allowed_tools`
- **tiny-mcp-server / tiny-mcp-registry** — sibling discovery systems; manifest format aligns
- **tiny-validator** — manifest is validated against a JSON Schema (subset)
- **tiny-skill-lint** — pre-flight lint of every skill file before registration
- **dev-masterkit** — the curated collection; this guide lives there

## Adoption Path

1. `pip install tiny-skill-loader`
2. Create a `skills/` directory; each file is a `MANIFEST` + `register(reg, manifest)`
3. `reg = SkillRegistry(); [reg.register_skill(s) for s in discover_skills(["./skills/"])`
4. Use `reg.call_tool("skill.tool_name", ...)` from your agent loop
5. Add `reg.list_tools()` to your LLM system prompt so it knows what's available
6. Lint every skill with `tiny-skill-lint` in CI before registration
7. Wrap the call site with `tiny-agent-scope` to enforce `allowed_tools` against `reg.list_tools()`

## Roadmap (next 7 days)

- `tiny-skill-loader` v0.1.1 — bug-fix release if any zero-dep issues surface
- `tiny-skill-loader` v0.2.0 — async skill loading; warm-up hooks
- `tiny-skill-pack` — `.skill` zip packaging (manifest + `*.py` + `README.md` + tests) is the next sibling
- `dev-masterkit` — `skills/` itself becomes a `tiny-skill-loader` discoverable directory

## See also

- [dev-reports/2026-10-10-developer-tool-trends.md](../../dev-reports/2026-10-10-developer-tool-trends.md) — "The manifest pattern" (Pattern 3)
- [tiny-tool-result-guide.md](./tiny-tool-result-guide.md) — the envelope every `call_tool` returns
- [tiny-agent-scope-guide.md](./tiny-agent-scope-guide.md) — the guardrail that wraps every `call_tool` invocation
- [tiny-skill-lint-guide.md](./tiny-skill-lint-guide.md) — pre-flight linter for every skill file
- [MEMORY.md](../../MEMORY.md) — Tiny-* stack overview (50+ repos)
