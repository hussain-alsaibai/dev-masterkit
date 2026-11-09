#!/usr/bin/env python3
"""
Ecosystem smoke test for the tiny-* package family.

WHY THIS EXISTS
---------------
Every tiny-* README carries a 25-entry "Ecosystem" list. On 2026-11-09 that
list was checked by actually installing each entry, and it did not survive:

  * 13 of 25 advertised packages ship no pyproject.toml and no setup.py, so
    `pip install git+https://github.com/hussain-alsaibai/<name>.git` fails
    with "does not appear to be a Python project".
  * 3 of those READMEs tell the reader to run `pip install <name>` where the
    name is owned on PyPI by a different maintainer. The command succeeds and
    installs someone else's code.

Neither defect is visible from inside the individual repo. Each one has its
own green CI badge, and no repo's CI can examine another repo. The failure is
only visible from the position a user occupies: following the advertised path.

This script takes that position. For each package in the list it answers
three questions that each README implicitly promises:

  INSTALL   Does the repository actually build a wheel?
  SHIP      Does that wheel contain the module, or only dist-info?
  IMPORT    Does the installed distribution import under the advertised name?
  NAME      Is the short name free on PyPI, or owned by someone else?

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not install from PyPI for packages that are not published. It checks
PyPI ownership only to warn, because "the name is taken" is a fact about the
registry, not about the repo -- but a README that says `pip install <name>`
for a squatted name is a real defect in the README.

USAGE
-----
    python3 ecosystem_smoke.py                 # all packages, live network
    python3 ecosystem_smoke.py --only tiny-queue tiny-flags
    python3 ecosystem_smoke.py --offline       # local clones only, no pip/PyPI
    python3 ecosystem_smoke.py --manifest my.txt

Exit 1 if any package fails INSTALL, SHIP or IMPORT. PyPI ownership is a WARN
by default; pass --strict-names to make it fatal.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

OWNER = "hussain-alsaibai"

# The advertised list, as it appears on every tiny-* README. Kept explicit
# rather than scraped: the point is to test what is *claimed*, and a scraper
# would silently follow the list if someone edited it to drop a broken entry.
DEFAULT_MANIFEST = [
    "tiny-router",
    "tiny-log",
    "tiny-validator",
    "tiny-config",
    "tiny-cli",
    "fast-cache",
    "tiny-rate",
    "tiny-retry",
    "tiny-pool",
    "tiny-agent",
    "tiny-mcp",
    "tiny-mcp-skel",
    "tiny-embed",
    "tiny-compose",
    "tiny-trace",
    "tiny-secret",
    "tiny-cron",
    "tiny-flags",
    "tiny-queue",
    "tiny-metrics",
    "tiny-timeout",
    "tiny-idempotency",
    "tiny-eventbus",
    "tiny-dist-audit",
    "tiny-worktree",
]

# Package name -> importable module. Derived rather than guessed: hyphens
# become underscores, with a few historical exceptions spelled out here.
MODULE_OVERRIDES = {
    "fast-cache": "fast_cache",
    "tiny-mcp-skel": "tiny_mcp_skel",
}

PYPI_TIMEOUT = 8


class Finding:
    def __init__(self, pkg: str, level: str, code: str, detail: str) -> None:
        self.pkg = pkg
        self.level = level  # FAIL | WARN | ok
        self.code = code
        self.detail = detail

    def __str__(self) -> str:
        return f"[{self.level:4}] {self.pkg:20} {self.code:12} {self.detail}"


def module_name(pkg: str) -> str:
    return MODULE_OVERRIDES.get(pkg, pkg.replace("-", "_"))


def run(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=600
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def has_packaging(path: str) -> bool:
    return os.path.exists(os.path.join(path, "pyproject.toml")) or os.path.exists(
        os.path.join(path, "setup.py")
    )


def wheel_ships_module(wheel_path: str, module: str) -> Tuple[bool, List[str]]:
    """A wheel can build successfully and contain only dist-info."""
    import zipfile

    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
    tops = {n.split("/")[0] for n in names}
    if f"{module}.py" in tops:
        return True, names
    if any(n.startswith(f"{module}/") for n in names):
        return True, names
    return False, names


def pypi_owner(name: str) -> Optional[str]:
    """Return an owner string if the name exists on PyPI, else None."""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=PYPI_TIMEOUT) as resp:
            info = json.load(resp).get("info", {})
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return None
    except json.JSONDecodeError:
        return None
    author = (info.get("author") or "").strip()
    email = (info.get("author_email") or "").strip()
    if not author and not email:
        return "unknown"
    return f"{author} <{email}>" if email else author


def check_local_clone(pkg: str, root: str) -> List[Finding]:
    """Offline path: inspect a local clone without pip or the network."""
    findings: List[Finding] = []
    path = os.path.join(root, "repos", pkg)
    if not os.path.isdir(path):
        findings.append(Finding(pkg, "WARN", "NO-CLONE", f"{path} not present"))
        return findings
    if not has_packaging(path):
        findings.append(
            Finding(pkg, "FAIL", "NO-PACKAGING", "no pyproject.toml or setup.py")
        )
        return findings
    mod = module_name(pkg)
    if not os.path.exists(os.path.join(path, f"{mod}.py")) and not os.path.isdir(
        os.path.join(path, mod)
    ):
        findings.append(
            Finding(pkg, "FAIL", "NO-MODULE", f"expected {mod}.py beside the metadata")
        )
    else:
        findings.append(Finding(pkg, "ok", "PACKAGED", f"ships {mod}"))
    return findings


def check_remote(pkg: str) -> List[Finding]:
    """Live path: build the wheel from GitHub, prove it ships the module."""
    findings: List[Finding] = []
    url = f"git+https://github.com/{OWNER}/{pkg}.git"
    mod = module_name(pkg)
    workdir = tempfile.mkdtemp(prefix=f"eco-{pkg}-")
    try:
        code, out = run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", workdir, url]
        )
        if code != 0:
            if "does not appear to be a Python project" in out:
                findings.append(
                    Finding(
                        pkg, "FAIL", "NO-PACKAGING", "pip wheel: not a Python project"
                    )
                )
            else:
                tail = out.strip().splitlines()[-1] if out.strip() else "unknown"
                findings.append(Finding(pkg, "FAIL", "BUILD-FAILED", tail[:100]))
            return findings

        wheels = glob.glob(os.path.join(workdir, "*.whl"))
        if not wheels:
            findings.append(Finding(pkg, "FAIL", "NO-WHEEL", "build produced no wheel"))
            return findings

        ok, names = wheel_ships_module(wheels[0], mod)
        if not ok:
            findings.append(
                Finding(
                    pkg,
                    "FAIL",
                    "EMPTY-WHEEL",
                    f"{mod} absent; wheel holds {len(names)} entries (dist-info only?)",
                )
            )
            return findings

        target = os.path.join(workdir, "site")
        code, out = run(
            [sys.executable, "-m", "pip", "install", "--no-deps", "--target", target, wheels[0]]
        )
        if code != 0:
            tail = out.strip().splitlines()[-1] if out.strip() else "unknown"
            findings.append(Finding(pkg, "FAIL", "INSTALL-FAILED", tail[:100]))
            return findings

        code, out = run(
            [
                sys.executable,
                "-c",
                f"import sys; sys.path.insert(0, {target!r}); import {mod}; "
                f"print(getattr({mod}, '__version__', '?'))",
            ]
        )
        if code != 0:
            findings.append(
                Finding(pkg, "FAIL", "IMPORT-FAILED", out.strip().splitlines()[-1][:100])
            )
            return findings

        version = out.strip().splitlines()[-1] if out.strip() else "?"
        findings.append(Finding(pkg, "ok", "IMPORTS", f"{mod} {version}"))
        return findings
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def readme_install_lines(
    pkg: str, root: str, owners: Optional[Dict[str, Optional[str]]] = None
) -> List[Finding]:
    """Flag a README that tells the reader to pip-install a name we do not own.

    `owners` is resolved once by the caller so this stays network-free and
    works under --offline.
    """
    findings: List[Finding] = []
    path = os.path.join(root, "repos", pkg, "README.md")
    if not os.path.exists(path):
        return findings
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    # A `pip install <name>` line is only a defect when the name is not ours.
    # If the name is free on PyPI the instruction is merely aspirational.
    squatted = (owners or {}).get(pkg)
    if not squatted:
        return findings
    # Several READMEs already warn about the squat themselves, in an HTML
    # comment or a blockquote, using different wording. Detect the *warning*,
    # not one exact phrase: if the README names the collision anywhere, the
    # reader has been told, and this is not a defect.
    already_warns = re.search(
        rf"(do not run|belongs to a different project|name on pypi|"
        rf"would fetch that package|installing `?pip install {re.escape(pkg)}`? would)",
        text,
        re.IGNORECASE,
    )
    if already_warns:
        return findings
    if re.search(rf"^\s*pip install {re.escape(pkg)}\s*$", text, re.MULTILINE):
        findings.append(
            Finding(
                pkg,
                "WARN",
                "SQUAT-CMD",
                f"README says 'pip install {pkg}' but PyPI has {squatted}",
            )
        )
    return findings


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", default=None)
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--strict-names", action="store_true")
    parser.add_argument(
        "--root",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.manifest:
        with open(args.manifest, encoding="utf-8") as fh:
            packages = [
                ln.strip()
                for ln in fh
                if ln.strip() and not ln.strip().startswith("#")
            ]
    else:
        packages = list(DEFAULT_MANIFEST)

    if args.only:
        wanted = set(args.only)
        packages = [p for p in packages if p in wanted]
        unknown = wanted - set(packages)
        if unknown:
            print(f"not in the manifest: {sorted(unknown)}", file=sys.stderr)
            return 2

    # Resolve PyPI ownership once. In offline mode we cannot ask, and we must
    # not: --offline means no network at all, not "no network except PyPI".
    owners: Dict[str, Optional[str]] = {}
    if not args.offline:
        for pkg in packages:
            owners[pkg] = pypi_owner(pkg)

    findings: List[Finding] = []
    for pkg in packages:
        if args.offline:
            findings.extend(check_local_clone(pkg, args.root))
        else:
            findings.extend(check_remote(pkg))
        findings.extend(readme_install_lines(pkg, args.root, owners))

    fails = [f for f in findings if f.level == "FAIL"]
    warns = [f for f in findings if f.level == "WARN"]
    ok = [f for f in findings if f.level == "ok"]

    for f in findings:
        print(f)

    print()
    print(
        f"{len(packages)} packages: {len(ok)} ok, {len(warns)} warn, {len(fails)} fail"
    )

    if fails:
        print("\nFAIL is fatal: a package the ecosystem advertises cannot be installed.")
        return 1
    if warns and args.strict_names:
        print("\nWARN is fatal under --strict-names.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
