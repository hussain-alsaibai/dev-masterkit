#!/usr/bin/env python3
"""
Check that every Python package's 'requires-python' matches its CI matrix.

The idea is taken from MakazhanAlpamys/Soup, whose
tests/test_requires_python_bound.py derives the bound from the CI matrix
instead of hardcoding it. The reasoning matters:

  * 'requires-python = ">=3.8"' with no ceiling tells pip that every future
    Python is supported. It is not.
  * A floor with no CI below it is a claim nobody tested. Our own AGENTS.md
    records the failure this catches: a package declared '>=3.8' and called
    asyncio.to_thread, which is 3.9+. The package shipped because CI was
    red and nobody read the badge.
  * A floor that the CI matrix does not cover is the same claim with no
    evidence behind it.

So for every package this script can find, it compares:

  the floor in pyproject.toml   against   the oldest Python in the CI matrix

and reports three kinds of problem:

  FAIL  the floor is below the oldest Python the CI matrix tests, so the
        declared support is untested.
  FAIL  the package declares a floor but has no CI workflow at all, so
        nothing tests the declared support.
  WARN  the package has a CI workflow but the matrix could not be parsed, so
        the check could not run for it.

A package with no CI is a FAIL, not a WARN: a version claim that is never
executed is exactly the defect this script exists to surface.

Exit code 1 on any FAIL, so CI fails loudly.

Usage:
    python3 scripts/check_python_support.py [--root DIR] [--json]

--root defaults to the parent of the directory holding this script's parent
(the 'repos' directory next to dev-masterkit), and also accepts a single
package directory.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)

# 'requires-python = ">=3.8"' / 'requires-python = ">=3.8,<4"'
REQUIRES_PYTHON = re.compile(
    r"""^\s*requires-python\s*=\s*["'](?P<spec>[^"']+)["']""",
    re.MULTILINE,
)

# A Python version list in a GitHub Actions workflow. The key is not always
# 'python-version': snapdb's matrix uses 'python:', and the version list can
# sit on the matrix definition rather than on the setup-python step. Both
# places are read, and only lines that carry an actual version list count.
PY_VERSION_LINE = re.compile(
    r"^\s*(?:python-version|python-versions|python|py)\s*:\s*(?P<value>.+)$",
    re.MULTILINE,
)
VERSION_TOKEN = re.compile(r"\b3\.\d{1,2}\b")

# '>=3.8' -> (3, 8)
FLOOR = re.compile(r">=\s*3\.(\d{1,2})")


def parse_floor(spec):
    """Return the (major, minor) floor in a requires-python spec, or None."""
    m = FLOOR.search(spec)
    if not m:
        return None
    return (3, int(m.group(1)))


def find_workflow_files(pkg_dir):
    """All GitHub Actions workflow files in a package."""
    wf = os.path.join(pkg_dir, ".github", "workflows")
    if not os.path.isdir(wf):
        return []
    out = []
    for name in sorted(os.listdir(wf)):
        if name.endswith((".yml", ".yaml")):
            out.append(os.path.join(wf, name))
    return out


def matrix_versions(pkg_dir):
    """
    Return (versions, parsed_ok) for a package.

    versions   sorted list of (major, minor) tuples found in CI workflows
    parsed_ok  False when there are workflows but no python-version was found
    """
    versions = set()
    workflows = find_workflow_files(pkg_dir)
    if not workflows:
        return [], False

    for wf in workflows:
        try:
            with open(wf, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for line in PY_VERSION_LINE.findall(text):
            for tok in VERSION_TOKEN.findall(line):
                major, minor = tok.split(".")
                versions.add((int(major), int(minor)))

    return sorted(versions), bool(versions)


def find_packages(root):
    """Locate candidate Python packages under root."""
    pkgs = []

    # A single package directory.
    if os.path.isfile(os.path.join(root, "pyproject.toml")):
        pkgs.append(root)
        return pkgs

    # A directory of packages: any subdirectory with a pyproject.toml.
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path):
            continue
        if os.path.isfile(os.path.join(path, "pyproject.toml")):
            pkgs.append(path)

    return pkgs


def check_package(pkg_dir):
    """Return a dict describing one package's support-claim health."""
    pyproject = os.path.join(pkg_dir, "pyproject.toml")
    name = os.path.basename(pkg_dir)

    with open(pyproject, encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    m = REQUIRES_PYTHON.search(text)
    if not m:
        return {
            "name": name,
            "path": pkg_dir,
            "status": "PASS",
            "detail": "no requires-python declared",
            "floor": None,
            "ci_versions": [],
        }

    spec = m.group("spec")
    floor = parse_floor(spec)
    versions, parsed_ok = matrix_versions(pkg_dir)

    result = {
        "name": name,
        "path": pkg_dir,
        "spec": spec,
        "floor": "%d.%d" % floor if floor else None,
        "ci_versions": ["%d.%d" % v for v in versions],
        "status": "PASS",
        "detail": "",
    }

    if not versions:
        result["status"] = "FAIL"
        result["detail"] = (
            "declares requires-python=%s but has no CI workflow that runs "
            "Python, so the declared support is untested" % spec
        )
        return result

    if floor is None:
        result["status"] = "WARN"
        result["detail"] = (
            "requires-python=%s has no >= floor this check could compare "
            "against the CI matrix" % spec
        )
        return result

    oldest = min(versions)
    if floor < oldest:
        result["status"] = "FAIL"
        result["detail"] = (
            "requires-python=%s claims support for %d.%d, but CI only tests "
            "%d.%d and up -- the claimed support is untested"
            % (spec, floor[0], floor[1], oldest[0], oldest[1])
        )
        return result

    if not parsed_ok:
        result["status"] = "WARN"
        result["detail"] = "could not parse the CI matrix"

    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        default=None,
        help="directory holding Python packages (default: ../repos next to dev-masterkit)",
    )
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    if args.root:
        root = os.path.abspath(args.root)
    else:
        candidates = [
            os.path.join(os.path.dirname(REPO_ROOT), "repos"),
            os.path.join(REPO_ROOT, "repos"),
        ]
        root = next(
            (c for c in candidates if os.path.isdir(c)),
            os.path.join(os.path.dirname(REPO_ROOT), "repos"),
        )

    if not os.path.isdir(root):
        print("no package root found at %s" % root, file=sys.stderr)
        return 2

    pkgs = find_packages(root)
    if not pkgs:
        print("no Python packages found under %s" % root, file=sys.stderr)
        return 2

    results = [check_package(p) for p in pkgs]
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]

    if args.json:
        print(json.dumps(results, indent=2))
        return 1 if fails else 0

    print("Checked %d Python packages under %s" % (len(results), root))
    print("  PASS %d   FAIL %d   WARN %d" % (
        len(results) - len(fails) - len(warns), len(fails), len(warns)))

    for r in fails + warns:
        print("")
        print("%-6s %s" % (r["status"], r["name"]))
        print("       %s" % r["detail"])
        if r.get("ci_versions"):
            print("       CI matrix: %s" % ", ".join(r["ci_versions"]))

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
