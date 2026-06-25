# doc-generator — Skill for Generating README + Docs

## Trigger

Use when the user asks to:
- "Write a README"
- "Generate documentation"
- "Create docs for my project"
- "Write API documentation"
- "Make my repo look professional"

## Description

Generates comprehensive, professional documentation from code analysis and
user context. Produces README.md, API docs, and usage guides that are accurate,
well-formatted, and immediately useful.

## Procedure

### 1. Gather Context

Before writing, collect:
- Source code structure (tree view)
- Public API surface (functions, classes, modules)
- Entry points / CLI commands and their arguments
- Installation requirements (Python version, optional deps)
- Project purpose and target audience
- Any existing docs or examples to reference

### 2. Generate README.md

Structure (in order):

```markdown
# {Project Name}

{One-line description}

{Badge block: CI status, version, license, Python versions}

## Features

- Bullet list of key capabilities
- What makes it different/better
- Performance or simplicity claims (if true)

## Installation

```bash
pip install {package-name}
```

Or from source:

```bash
git clone https://github.com/{user}/{repo}.git
cd {repo}
pip install -e .
```

## Quick Start

Minimal working example. Copy-paste ready.

```python
from {package} import {main_function}

result = {main_function}("example input")
print(result)
```

## Usage

### As a Library

```python
import {package}

# Describe common use cases
obj = {package}.{Class}()
obj.method()
```

### CLI

```bash
{command} --help
{command} --input file.txt --output result.json
```

## API Reference

### `{function_name}({signature})`

{Description}

- **Parameters:**
  - `param1` ({type}): Description
- **Returns:** {type} — Description
- **Raises:** {Exception} — When/why

### `{ClassName}`

{Description}

- **Methods:**
  - `method_name()`: Description

## Development

```bash
# Run tests
python -m unittest discover -v

# Install in editable mode
pip install -e .
```

## License

{License name} — see [LICENSE](LICENSE) file.
```

### 3. Generate API Documentation

For each public function/class, extract:
- Docstring (first line = summary, rest = details)
- Type hints from signature
- Default parameter values
- Exceptions raised

Format as Markdown with anchors for linking.

### 4. Generate Examples

Create `docs/examples.md` with:
- Basic usage (the "hello world")
- Common patterns (the "80% use case")
- Advanced usage (edge cases, tuning)
- Troubleshooting (common errors and fixes)

### 5. Generate Contributing Guide (Optional)

If open-source or team project, create `CONTRIBUTING.md`:
- How to set up dev environment
- How to run tests
- How to submit changes
- Code style conventions

### 6. Validate Documentation

- [ ] All code examples are copy-paste ready and tested
- [ ] All links are valid (internal anchors, external URLs)
- [ ] All badges use correct URLs
- [ ] Installation instructions work on fresh environment
- [ ] Screenshots/diagrams have alt text (if applicable)

## Example

**User:** "Document my `url-cleaner` package."

**Generated README.md includes:**
- Badges: tests passing, PyPI version, MIT license, Python 3.9+
- Features: zero dependencies, CLI + library, idempotent normalization
- Quick start: 3-line Python example + bash example
- API: `normalize_url()`, `is_valid_url()`, `UrlCleaner` class
- Development: `python -m unittest discover`

## Validation Checklist

- [ ] README has all sections: Features, Installation, Quick Start, Usage, API, Development, License
- [ ] All code examples tested and working
- [ ] API reference covers all public functions/classes
- [ ] Links are valid (no 404s)
- [ ] Badges render correctly on GitHub
- [ ] Installation instructions tested on clean environment
- [ ] Examples demonstrate real, useful behavior (not `foo`/`bar` placeholders)

## Notes

- Use badges from shields.io: `https://img.shields.io/badge/...`
- Keep README under 200 lines if possible; move long API docs to separate files
- Include a Table of Contents for READMEs over 100 lines
- Use `python -m doctest` to validate inline code examples where applicable
- For CLI tools, always include `--help` output
