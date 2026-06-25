# /scaffold Command

## Trigger

User types: `/scaffold`, `/scaffold <project-name>`, or "Create a repo called <name>"

## Description

Scaffolds a new zero-dependency Python project from a template. Creates directory
structure, core files, tests, CI config, and initializes git.

## Usage

```
/scaffold <project-name> [--cli] [--web] [--ci] [--pre-commit]
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `project-name` | Repository name (kebab-case) | Required |
| `--cli` | Include CLI entry point | False |
| `--web` | Include web/API scaffold | False |
| `--ci` | Include GitHub Actions CI | True |
| `--pre-commit` | Include pre-commit config | False |

## Workflow

1. **Validate name** — ensure kebab-case, no special chars
2. **Create directories** — `src/{name}/`, `tests/`, `docs/`, `.github/workflows/`
3. **Generate files**:
   - `pyproject.toml` — modern Python packaging
   - `src/{name}/__init__.py` — version + exports
   - `src/{name}/main.py` — entry point (CLI or module)
   - `tests/test_main.py` — unittest suite
   - `.github/workflows/ci.yml` — cross-platform CI
   - `.gitignore` — standard Python
   - `README.md` — basic template
   - `LICENSE` — MIT
4. **Validate** — `python -m unittest discover`, `python -m py_compile`
5. **Initialize git** — `git init && git add . && git commit -m "feat: initial scaffold"`
6. **Present** — show tree, explain next steps

## Example

**User:** `/scaffold url-cleaner --cli`

**Result:**
```
Created url-cleaner/
├── src/
│   └── url_cleaner/
│       ├── __init__.py
│       └── main.py          # CLI with argparse
├── tests/
│   └── test_main.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore

Tests pass: ✅
Git initialized: ✅

Next: cd url-cleaner && pip install -e .
```

## Notes

- Uses `repo-creator` skill for file generation
- All files use zero third-party dependencies
- Compatible with Python 3.9+
