# tiny-skill-loader

> **Runtime skill/extension loader for AI agents.** Discover, validate, mount, and call plugin "skills" from a directory of single-file Python modules. Zero deps, single file, MIT.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](#)
[![Zero deps](https://img.shields.io/badge/dependencies-zero-success.svg)](#)
[![Tests](https://img.shields.io/badge/tests-26%20passing-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Why?

AI agents grow by accumulating *skills*: one module that scrapes Jira, another that summarizes a URL, a third that calls your internal billing API. After a year you have 30 of them. Now you need a loader that:

- Discovers them by file/directory glob
- Validates a manifest (name, version, description, tags)
- Calls each module's `register(registry, manifest)` to wire tools into the agent
- Lets the agent's tool-call layer route by name: `reg.call_tool("jira.search", query="...")`
- Surfaces what got loaded (`reg.list_skills()`, `reg.list_tools()`)

`tiny-skill-loader` is that loader, in one file, ~260 LOC.

## Quick Start

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
| `name` | str | yes | Unique skill identifier |
| `version` | str | yes | Semver string |
| `description` | str | yes | One-line summary |
| `author` | str | no | Author/email |
| `tags` | list | no | Free-form search tags |
| `requires` | list | no | Other skill/package names |

The `register(reg, manifest)` function is optional. If present, it should call `reg.tool(name, fn)` or use the `@reg.tool("name")` decorator.

## API

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

### Exceptions
- `SkillLoadError(message)` — manifest invalid, duplicate tool, file syntax error, etc.

## Why "tiny"?

Part of the OpenClaw zero-dep, single-file ecosystem: `tiny-llm`, `tiny-llm-router`, `tiny-tool-result`, `tiny-agent-scope`, `tiny-semantic-cache`, `tiny-cost`, `tiny-trace`, `tiny-trace-otel`, `tiny-event-bus`, `tiny-router`, `tiny-config`, `tiny-log`, `tiny-validator`, `tiny-cli`, `tiny-rate-limiter`, `tiny-circuit-breaker`, `tiny-retry-plus`, `tiny-workflow-engine`, `tiny-scheduler`, and 50+ more.

## License

MIT — copy-paste, modify, ship.
