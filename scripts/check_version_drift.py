#!/usr/bin/env python3
"""Find a repository whose stated version disagrees with itself.

A version stated in more than one file is a version stated once and guessed
everywhere else. The guard that covers it usually exists -- and it reads the
pair its author was thinking about, which is almost never the file that
drifted. `snapdb` had `tests/test_version_consistency.py` (pyproject vs
`__version__`, semver) and passed it while the `package.json` beside it was
**seven minor releases** stale. `tiny-router` was five releases stale with no
guard at all.

This is the machine check behind prompt
`a-version-guard-only-covers-the-files-it-reads.md` (2026-11-05).

What it reads, per repository root:

  pyproject.toml  [project] version  (or [tool.poetry] version)
  package.json    version
  <pkg>/__init__.py  __version__ = "..."

What it compares: every pair that exists. Files that do not exist are not a
finding -- a one-surface repository cannot drift from itself.

Usage:
    python3 scripts/check_version_drift.py --repo .            # one repo
    python3 scripts/check_version_drift.py --root ~/github     # siblings
    python3 scripts/check_version_drift.py --repo . --json

Exit codes:
    0  every stated version agrees (or only one statement exists)
    1  at least one repository states two different versions
    2  usage error (no root given, or no repositories found)

Zero dependencies. Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKIP_DIRS = {
    ".git", "__pycache__", ".tox", ".nox", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "build", "dist", "node_modules", ".venv", "venv",
}

# Semver-ish, with an optional pre-release/build tail. Deliberately permissive:
# a strict parser here would skip exactly the malformed versions worth seeing.
VERSION_RE = re.compile(r'^v?(\d+\.\d+(?:\.\d+)?)([-+][0-9A-Za-z.\-+]+)?$')

PYPROJECT_PROJECT_RE = re.compile(
    r'^\[project\]\s*$(.*?)(?=^\[|\Z)', re.MULTILINE | re.DOTALL)
PYPROJECT_POETRY_RE = re.compile(
    r'^\[tool\.poetry\]\s*$(.*?)(?=^\[|\Z)', re.MULTILINE | re.DOTALL)
VERSION_LINE_RE = re.compile(r'^\s*version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
DUNDER_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def version_from_pyproject(root):
    """Return (version, source) from pyproject.toml, or (None, None).

    [project] wins over [tool.poetry]: a file carrying both is using the
    PEP 621 table as the build input, and that is the one pip reads.
    """
    path = os.path.join(root, "pyproject.toml")
    text = _read(path)
    if text is None:
        return None, None
    for table, source in ((PYPROJECT_PROJECT_RE, "pyproject.toml [project]"),
                          (PYPROJECT_POETRY_RE, "pyproject.toml [tool.poetry]")):
        match = table.search(text)
        if match:
            found = VERSION_LINE_RE.search(match.group(1))
            # `version = { attr = "..." }` and `dynamic = ["version"]` are
            # deliberate indirection, not a stated version. Skip, do not guess.
            if found:
                return found.group(1).strip(), source
    return None, None


def version_from_package_json(root):
    path = os.path.join(root, "package.json")
    text = _read(path)
    if text is None:
        return None, None
    try:
        data = json.loads(text)
    except ValueError:
        return None, None
    value = data.get("version")
    if isinstance(value, str) and value.strip():
        return value.strip(), "package.json"
    return None, None


def version_from_dunder(root):
    """Find __version__ in the top-level package's __init__.py."""
    candidates = []
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        return None, None
    for entry in entries:
        if entry.startswith(".") or entry in SKIP_DIRS:
            continue
        init = os.path.join(root, entry, "__init__.py")
        if os.path.isfile(init):
            candidates.append(init)
    if not candidates:
        return None, None
    # Prefer the package that carries a __version__ at all; if several do,
    # report the first in sorted order so the output is stable between runs.
    for init in candidates:
        text = _read(init) or ""
        found = DUNDER_RE.search(text)
        if found:
            rel = os.path.relpath(init, root)
            return found.group(1).strip(), rel
    return None, None


def normalise(version):
    """Strip a leading v and pad a two-component core to three.

    The pre-release/build tail is KEPT: `1.0.0-rc1` is not `1.0.0`, and a
    normaliser that strips every tail calls a release candidate equal to the
    release it never became.
    """
    match = VERSION_RE.match(version.strip())
    if not match:
        return version.strip().lower()
    core, tail = match.group(1), match.group(2) or ""
    if core.count(".") == 1:
        core += ".0"
    return (core + tail).lower()


def inspect_repo(root):
    """Return a dict describing every version surface found in one repo."""
    surfaces = []
    for getter in (version_from_pyproject, version_from_package_json, version_from_dunder):
        version, source = getter(root)
        if version:
            surfaces.append({"source": source, "version": version,
                             "normalised": normalise(version)})
    distinct = sorted({s["normalised"] for s in surfaces})
    return {
        "repo": os.path.basename(os.path.abspath(root)),
        "path": os.path.abspath(root),
        "surfaces": surfaces,
        "stale": len(distinct) > 1,
    }


def find_repos(root):
    """Yield repository roots directly under `root`, plus `root` itself."""
    if os.path.isfile(os.path.join(root, "pyproject.toml")) or \
            os.path.isfile(os.path.join(root, "package.json")):
        yield root
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        return
    for entry in entries:
        if entry.startswith(".") or entry in SKIP_DIRS:
            continue
        path = os.path.join(root, entry)
        if not os.path.isdir(path):
            continue
        if os.path.isfile(os.path.join(path, "pyproject.toml")) or \
                os.path.isfile(os.path.join(path, "package.json")):
            yield path


def render(report):
    """Human-readable summary. Always prints what was read, not just verdicts."""
    lines = []
    stale = [r for r in report if r["stale"]]
    for item in report:
        if not item["surfaces"]:
            continue
        if item["stale"]:
            detail = ", ".join("%s=%s" % (s["source"], s["version"])
                               for s in item["surfaces"])
            lines.append("DRIFT  %-28s %s" % (item["repo"], detail))
        elif len(item["surfaces"]) > 1:
            lines.append("ok     %-28s %s" % (item["repo"], item["surfaces"][0]["version"]))
    singles = [r for r in report if len(r["surfaces"]) == 1]
    lines.append("")
    lines.append("%d %s inspected, %d with two or more surfaces, %d drifting, "
                 "%d with a single surface (cannot drift)" % (
                     len([r for r in report if r["surfaces"]]),
                     "repository" if len(report) != 1 else "repository",
                     len([r for r in report if len(r["surfaces"]) > 1]),
                     len(stale), len(singles)))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", help="inspect a single repository root")
    parser.add_argument("--root", help="inspect every repository directly under this directory")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if args.repo:
        roots = [args.repo]
        if not os.path.isdir(args.repo):
            sys.stderr.write("not a directory: %s\n" % args.repo)
            return 2
    elif args.root:
        if not os.path.isdir(args.root):
            sys.stderr.write("not a directory: %s\n" % args.root)
            return 2
        roots = list(find_repos(args.root))
    else:
        parser.print_usage(sys.stderr)
        return 2

    report = [inspect_repo(r) for r in roots]
    stated = [r for r in report if r["surfaces"]]
    if not stated:
        sys.stderr.write("no stated versions found under %s\n"
                         % (args.repo or args.root))
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render(report))
    return 1 if any(r["stale"] for r in stated) else 0


if __name__ == "__main__":
    sys.exit(main())
