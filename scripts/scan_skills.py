#!/usr/bin/env python3
"""
Security scan for the skills in this repository, using NVIDIA SkillSpector.

Why this exists
---------------
SkillSpector's suppression baseline is bound to the scanner version. When the
scanner is upgraded, every fingerprint in the baseline changes, and a stale
baseline silently suppresses NOTHING. The symptom is a report that lists 100+
"new" findings that a human already reviewed and accepted on an earlier day.

That happened here: the baseline was written against scanner 2.13.1, the
scanner moved to 2.13.2, and the next scan reported 124 unsuppressed
findings, none of them new. Nobody noticed, because the baseline was a
gitignored local file and no CI job consumed it.

This script closes that hole:

  * it pins the scanner to the version the baseline was generated with
  * it fails if the installed scanner version does not match the baseline
  * it fails if any finding survives the baseline (a genuinely new finding)

The baseline is committed on purpose. It is a record of human review
decisions, and it only works if it is versioned alongside the skills.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(ROOT, ".skillspector-baseline.yaml")
REPORT = os.path.join(ROOT, ".skillspector-report.json")

# The scanner version this baseline was generated with. Bump it in the same
# commit that regenerates the baseline, never on its own.
PINNED_SCANNER = "2.13.2"


def fail(msg):
    print("FAIL: %s" % msg)
    sys.exit(1)


def resolve_scanner():
    """Return the path to a runnable scanner binary.

    Do NOT trust PATH alone. More than one skillspector install can exist on a
    host, and they can be built against different Pythons. A stale install
    linked to Python 3.11 fails to start at all, and the message it prints is
    'requires a different Python' - which reads like a missing interpreter
    problem rather than the wrong-binary problem it actually is.

    Preference order:
      1. $SKILLSPECTOR_BIN, if set (CI and anyone with an unusual layout)
      2. a venv alongside this repository (.ssvenv / .venv), then one inside it
      3. whatever PATH resolves to
    """
    override = os.environ.get("SKILLSPECTOR_BIN")
    if override:
        if not (os.path.isfile(override) and os.access(override, os.X_OK)):
            fail("SKILLSPECTOR_BIN=%s is not an executable file" % override)
        return override

    # A local venv may sit beside the repo rather than inside it: the workspace
    # owns .ssvenv, and dev-masterkit is a sibling of it.
    roots = [ROOT, os.path.dirname(ROOT)]
    for base in roots:
        for venv in (".ssvenv", ".venv", "venv"):
            for rel in ("bin/skillspector", "Scripts/skillspector.exe"):
                cand = os.path.join(base, venv, rel)
                if os.path.isfile(cand) and os.access(cand, os.X_OK):
                    return cand

    found = shutil.which("skillspector")
    if found:
        return found

    fail(
        "skillspector is not installed. Install it with:\n"
        "  pip install 'git+https://github.com/NVIDIA/SkillSpector@"
        + PINNED_SCANNER
        + "'"
    )


def scanner_version(scanner):
    try:
        proc = subprocess.run(
            [scanner, "--version"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail("%s disappeared between resolution and execution" % scanner)
    except OSError as exc:
        fail("could not execute %s: %s" % (scanner, exc))

    out = (proc.stdout + "" + proc.stderr).strip()
    if proc.returncode != 0:
        # The interpreter-version error arrives here, not as a crash. Say what
        # it means instead of passing through a message that blames Python.
        fail(
            "%s could not run (exit %d): %s\n"
            "  This usually means the install is bound to a Python the package "
            "does not support (SkillSpector needs >=3.12).\n"
            "  Point at a working install with SKILLSPECTOR_BIN=/path/to/skillspector"
            % (scanner, proc.returncode, out[:600])
        )
    m = re.search(r"(\d+\.\d+\.\d+)", out)
    if not m:
        fail("could not parse a version out of %r" % out)
    return m.group(1)


def baseline_version():
    if not os.path.exists(BASELINE):
        fail(
            "the suppression baseline %s is missing. Generate it with:\n"
            "  skillspector baseline ./skills -o .skillspector-baseline.yaml --no-llm"
            % os.path.relpath(BASELINE, ROOT)
        )
    with open(BASELINE, encoding="utf-8") as fh:
        head = fh.read(4096)
    m = re.search(r"^scanner_version:\s*(\S+)", head, re.MULTILINE)
    if not m:
        fail("the baseline has no 'scanner_version:' key")
    return m.group(1).strip()


def main():
    scanner = resolve_scanner()
    installed = scanner_version(scanner)
    pinned = baseline_version()

    print("scanner: %s" % scanner)
    print("scanner installed: %s" % installed)
    print("baseline written for: %s" % pinned)

    if installed != pinned:
        fail(
            "scanner version %s does not match the baseline (%s). A stale "
            "baseline suppresses nothing, so every reviewed finding looks "
            "new. Regenerate the baseline with the pinned version and "
            "review the diff:\n"
            "  %s baseline ./skills -o .skillspector-baseline.yaml --no-llm"
            % (installed, pinned, scanner)
        )

    result = subprocess.run(
        [
            scanner,
            "scan",
            "./skills",
            "--no-llm",
            "--format",
            "json",
            "--baseline",
            BASELINE,
            "--output",
            REPORT,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        fail(
            "skillspector scan failed (exit %d): %s"
            % (result.returncode, result.stderr.strip()[:2000])
        )

    if not os.path.exists(REPORT):
        fail("skillspector produced no report")
    with open(REPORT, encoding="utf-8") as fh:
        report = json.load(fh)

    issues = report.get("issues", [])
    suppressed = report.get("suppressed_count", 0)
    assessment = report.get("risk_assessment", {})

    print(
        "findings: %d unsuppressed, %d suppressed, risk score %s (%s)"
        % (
            len(issues),
            suppressed,
            assessment.get("score"),
            assessment.get("severity"),
        )
    )

    try:
        os.remove(REPORT)
    except OSError:
        pass

    if issues:
        for issue in issues[:40]:
            loc = issue.get("location") or {}
            print(
                "  FAIL: %s %s %s:%s"
                % (
                    issue.get("severity"),
                    issue.get("id"),
                    loc.get("file"),
                    loc.get("start_line"),
                )
            )
        if len(issues) > 40:
            print("  ... and %d more" % (len(issues) - 40))
        fail(
            "%d finding(s) are not covered by the baseline. Review them, then "
            "either fix the skill or extend the baseline with a reason."
            % len(issues)
        )

    print("OK: every finding is covered by the reviewed baseline.")


if __name__ == "__main__":
    main()
