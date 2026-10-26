#!/usr/bin/env python3
"""
Structure check for dev-masterkit.

This repository is a collection of skills, prompts and reports. It has no test
suite, so nothing checked it. Two things were true and invisible:

  * 25 of the 35 SKILL.md files are legacy markdown documents with no YAML
    frontmatter. An agent runtime cannot load those as skills.
  * A skill that *does* declare frontmatter but omits 'name' or 'description'
    is silently unloadable too.

So this check has two levels:

  FAIL  A skill declares frontmatter but it is invalid, or a skill that is
        listed in skills/AGENTSKILLS_PENDING.md as needing conversion has
        already been converted but is still broken.
  WARN  A skill is still a legacy markdown document. It is listed in
        skills/AGENTSKILLS_PENDING.md, which is the tracked backlog.

Exit code 1 on any FAIL, so CI fails loudly. The backlog is reported but does
not fail the build, because converting 25 documents is a content change, not
a regression.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
PENDING_FILE = os.path.join(SKILLS_DIR, "AGENTSKILLS_PENDING.md")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# Directories that hold scripts and notes rather than skills. They are not
# expected to have a SKILL.md.
NON_SKILL_DIRS = {
    "accountability",
    "cost-tracker",
    "repo-monitor",
    "research",
    "self-reflection",
}

errors = []
warnings = []
pending = []

if not os.path.isdir(SKILLS_DIR):
    print("FAIL: no skills/ directory found")
    sys.exit(1)

# Read the tracked backlog, if present.
pending_set = set()
if os.path.exists(PENDING_FILE):
    for line in open(PENDING_FILE, encoding="utf-8"):
        line = line.strip()
        m = re.match(r"^-\s+\[([a-z0-9-]+)\]", line)
        if m:
            pending_set.add(m.group(1))

skills = sorted(
    d for d in os.listdir(SKILLS_DIR)
    if os.path.isdir(os.path.join(SKILLS_DIR, d))
)

for name in skills:
    if name in NON_SKILL_DIRS:
        continue

    skill_md = os.path.join(SKILLS_DIR, name, "SKILL.md")

    if not os.path.exists(skill_md):
        errors.append("skills/%s has no SKILL.md" % name)
        continue

    text = open(skill_md, encoding="utf-8").read()
    m = FRONTMATTER.match(text)

    if not m:
        # Legacy markdown document. Tracked as backlog, not a regression.
        pending.append(name)
        if name not in pending_set:
            errors.append(
                "skills/%s has no YAML frontmatter and is not listed in "
                "skills/AGENTSKILLS_PENDING.md" % name
            )
        continue

    block = m.group(1)
    fm_name = re.search(r"^name:\s*(.+)$", block, re.MULTILINE)
    fm_desc = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)

    if not fm_name:
        errors.append("skills/%s/SKILL.md frontmatter has no 'name'" % name)
    if not fm_desc:
        errors.append("skills/%s/SKILL.md frontmatter has no 'description'" % name)

    # The frontmatter 'name' is the canonical skill identifier and does not
    # have to match the directory name (for example skills/codebuddy-code
    # declares 'name: codebuddy-cli'). Only flag an empty one.

# Build artefacts must not be tracked.
try:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    for path in tracked:
        if "__pycache__/" in path or path.endswith(".pyc") or "node_modules/" in path:
            errors.append("tracked build artefact: %s" % path)
except Exception as exc:  # pragma: no cover
    warnings.append("could not list tracked files: %s" % exc)

print(
    "skills: %d total, %d loadable, %d pending frontmatter"
    % (len(skills) - len(NON_SKILL_DIRS), len(skills) - len(NON_SKILL_DIRS) - len(pending), len(pending))
)

if pending:
    warnings.append(
        "%d skill(s) are still legacy markdown and cannot be loaded as "
        "AgentSkills: %s" % (len(pending), ", ".join(pending))
    )

for w in warnings:
    print("WARN: %s" % w)

if errors:
    for e in errors:
        print("FAIL: %s" % e)
    print("\n%d problem(s) found." % len(errors))
    sys.exit(1)

print("OK: no broken skills, no tracked build artefacts.")
