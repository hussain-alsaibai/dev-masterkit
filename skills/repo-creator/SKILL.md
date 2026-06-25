# repo-creator — Skill for Creating Zero-Dependency Python Repos

## Trigger

Use when the user asks to:
- "Create a new repository" or "scaffold a project"
- "Set up a Python project"
- "Initialize a repo with [specific structure]"
- "Create a zero-dependency Python package"

## Description

Creates production-ready Python repositories with zero external dependencies.
All tooling is standard library only. The generated repo is immediately usable,
testable, and publishable.

## Procedure

### 1. Validate Request

Confirm with the user (or infer from context):
- Project name (kebab-case, e.g. `my-awesome-tool`)
- Python version target (default: 3.9+)
- Whether to include:
  - [ ] CLI entry point
  - [ ] Web/API module
  - [ ] GitHub Actions CI
  - [ ] Pre-commit hooks config

### 2. Create Directory Structure

```
{project-name}/
├── src/
│   └── {project_name}/
│       ├── __init__.py
│       └── main.py          # CLI or entry point
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
│   └── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── pyproject.toml           # Modern Python packaging
├── LICENSE
└── README.md
```

### 3. Generate Core Files

#### `pyproject.toml`
Use standard PEP 518/621 format with `[project]` table. No `setup.py`.
Include `scripts` or `gui-scripts` entry points if CLI requested.

#### `src/{project_name}/__init__.py`
Expose version via `__version__ = "0.1.0"`.

#### `src/{project_name}/main.py`
- If CLI: `argparse`-based main with `--version` flag
- If module: clean public API with docstrings

#### `tests/test_main.py`
Use only `unittest` (stdlib). One test class, minimal but real assertions.

#### `.gitignore`
Standard Python gitignore: `__pycache__/`, `*.egg-info/`, `.pytest_cache/`,
`build/`, `dist/`, `.env`, `.venv/`, `*.pyc`.

#### `.github/workflows/ci.yml`
Matrix: `ubuntu-latest`, `windows-latest`, `macos-latest`.
Python versions: 3.9, 3.10, 3.11, 3.12.
Steps: checkout → setup-python → `python -m unittest discover`.

### 4. Validate Locally

```bash
cd {project-name}
python -m unittest discover -v
python -m py_compile src/{project_name}/main.py
```

If any step fails, fix before presenting to user.

### 5. Initialize Git

```bash
git init
git add .
git commit -m "feat: initial project scaffold"
```

### 6. Present to User

Provide:
- Tree view of created files
- How to run tests: `python -m unittest discover`
- How to install in dev mode: `pip install -e .`
- Next steps (GitHub push, version bump, etc.)

## Example

**User:** "Create a repo called `url-cleaner` that normalizes URLs."

**Result:**
- `src/url_cleaner/__init__.py` — version 0.1.0
- `src/url_cleaner/main.py` — `normalize_url(url: str) -> str`, CLI via argparse
- `tests/test_main.py` — unittest with 3 test cases (http→https, trailing slash removal, invalid input handling)
- `pyproject.toml` — modern packaging, `url-cleaner = "url_cleaner.main:main"` script entry
- CI runs `python -m unittest discover` across 3 OS × 4 Python versions

## Validation Checklist

- [ ] `python -m py_compile` succeeds on all `.py` files
- [ ] `python -m unittest discover` passes (at least 1 test)
- [ ] `pip install -e .` installs package with correct entry point (if CLI)
- [ ] No third-party dependencies in `pyproject.toml` or source
- [ ] `.gitignore` covers standard Python artifacts
- [ ] README includes install + usage instructions

## Notes

- Prefer `src/` layout over flat layout for better test isolation
- Always use `pyproject.toml` — `setup.py` and `setup.cfg` are deprecated for new projects
- If user wants dependencies later, they can add to `pyproject.toml[project]dependencies`
- Keep `__init__.py` minimal; business logic belongs in dedicated modules
