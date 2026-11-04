#!/usr/bin/env python3
"""Find byte-identical Python modules shipped from more than one package.

A copy of a module is not a dependency. When the same file is published
twice, every defect fixed in one copy is still shipping in the other, and
the fix looks done because the repo you were reading has it.

This is the machine check behind prompt `one-fix-in-one-repo-is-not-a-fix.md`
and behind the tiny-safeexec / tiny-sandbox finding of 2026-11-04.

Usage:
    python3 scripts/check_duplicate_modules.py ~/github          # sibling roots
    python3 scripts/check_duplicate_modules.py --root ./repos --json

Exit codes:
    0  no duplicate modules found
    1  at least one module hash appears in more than one package
    2  usage error (no root given, or no packages found)

Zero dependencies. Python 3.8+.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

# Directories that never contain shipped source.
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".tox",
    ".nox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "node_modules",
    ".venv",
    "venv",
    "htmlcov",
}

# A module this small is boilerplate (empty __init__.py, version stubs,
# licence headers) and a match says nothing about duplicated code.
MIN_BYTES = 200


def find_modules(root):
    """Yield (package, path) for every .py file under a package root."""
    for pkg in sorted(os.listdir(root)):
        pkg_dir = os.path.join(root, pkg)
        if not os.path.isdir(pkg_dir) or pkg.startswith("."):
            continue
        if not os.path.exists(os.path.join(pkg_dir, "pyproject.toml")):
            continue
        for dirpath, dirnames, filenames in os.walk(pkg_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in sorted(filenames):
                if name.endswith(".py"):
                    yield pkg, os.path.join(dirpath, name)


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def collect(root, min_bytes=MIN_BYTES):
    """Map sha256 -> [(package, relpath, size)].

    A file is skipped when it is smaller than min_bytes or is a test file:
    two repos can legitimately ship the same generated test helper, and the
    question here is about shipped modules.
    """
    seen = {}
    packages = set()
    for pkg, path in find_modules(root):
        packages.add(pkg)
        size = os.path.getsize(path)
        if size < min_bytes:
            continue
        rel = os.path.relpath(path, os.path.join(root, pkg))
        base = os.path.basename(path)
        if base.startswith("test_") or base == "conftest.py":
            continue
        seen.setdefault(digest(path), []).append((pkg, rel, size))
    return seen, packages


def duplicates(seen, ignore_pairs=()):
    """Groups whose hash appears under more than one package name."""
    ignored = {frozenset(p) for p in ignore_pairs}
    groups = []
    for sha, hits in seen.items():
        pkgs = {pkg for pkg, _, _ in hits}
        if len(pkgs) < 2:
            continue
        if frozenset(pkgs) in ignored:
            continue
        groups.append({"sha256": sha, "packages": sorted(pkgs), "files": hits})
    groups.sort(key=lambda g: (g["packages"][0], g["sha256"][:8]))
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", help="directory holding sibling packages")
    ap.add_argument("--root", dest="root_opt", help="same as positional root")
    ap.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="A:B",
        help="declared duplicate pair to accept (repeatable)",
    )
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--min-bytes",
        type=int,
        default=MIN_BYTES,
        help="ignore files smaller than this (default %(default)s)",
    )
    args = ap.parse_args(argv)

    root = args.root_opt or args.root
    if not root:
        ap.error("a root directory is required")
        return 2
    root = os.path.abspath(os.path.expanduser(root))
    if not os.path.isdir(root):
        ap.error("not a directory: %s" % root)
        return 2

    seen, packages = collect(root, args.min_bytes)
    if not packages:
        print("no packages with a pyproject.toml under %s" % root, file=sys.stderr)
        return 2

    pairs = []
    for spec in args.ignore:
        left, _, right = spec.partition(":")
        if not right:
            ap.error("--ignore wants A:B, got %r" % spec)
        pairs.append((left, right))

    groups = duplicates(seen, pairs)

    if args.json:
        json.dump(
            {
                "root": root,
                "packages": len(packages),
                "modules": len(seen),
                "duplicates": groups,
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print(
            "scanned %d packages, %d distinct modules >= %d bytes"
            % (len(packages), len(seen), args.min_bytes)
        )
        for g in groups:
            print(
                "DUPLICATE %s  %s"
                % (g["sha256"][:12], " == ".join(g["packages"]))
            )
            for pkg, rel, size in g["files"]:
                print("    %-28s %s (%d bytes)" % (pkg, rel, size))

    return 1 if groups else 0


if __name__ == "__main__":
    sys.exit(main())
