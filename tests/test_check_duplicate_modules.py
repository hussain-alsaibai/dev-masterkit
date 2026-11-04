"""Tests for scripts/check_duplicate_modules.py.

Two of these tests are the reason the script exists:
`test_identical_modules_are_reported` fails against a scanner that only
looks at one package, and `test_declared_pair_is_ignorable` fails against
one that has no way to record a copy that admits it is a copy.

Run: python3 -m pytest tests/ -q
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "scripts", "check_duplicate_modules.py")

BODY = "def add(a, b):\n    return a + b\n" * 20


def make_pkg(root, name, module_text, filename="core.py"):
    pkg_dir = os.path.join(root, name)
    os.makedirs(os.path.join(pkg_dir, name.replace("-", "_")), exist_ok=True)
    with open(os.path.join(pkg_dir, "pyproject.toml"), "w") as fh:
        fh.write('[project]\nname = "%s"\n' % name)
    path = os.path.join(pkg_dir, name.replace("-", "_"), filename)
    with open(path, "w") as fh:
        fh.write(module_text)
    return path


def run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True,
        text=True,
    )


def test_identical_modules_are_reported(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY)
    make_pkg(str(tmp_path), "beta", BODY)
    proc = run(str(tmp_path))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "DUPLICATE" in proc.stdout
    assert "alpha" in proc.stdout and "beta" in proc.stdout


def test_distinct_modules_pass(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY)
    make_pkg(str(tmp_path), "beta", BODY.replace("add", "plus"))
    proc = run(str(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_declared_pair_is_ignorable(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY)
    make_pkg(str(tmp_path), "beta", BODY)
    proc = run(str(tmp_path), "--ignore", "alpha:beta")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "DUPLICATE" not in proc.stdout


def test_small_boilerplate_is_not_a_duplicate(tmp_path):
    # An empty-ish __init__.py in both repos is normal packaging, not a copy.
    make_pkg(str(tmp_path), "alpha", '"""alpha."""\n', filename="__init__.py")
    make_pkg(str(tmp_path), "beta", '"""alpha."""\n', filename="__init__.py")
    proc = run(str(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_test_files_are_not_counted(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY, filename="test_core.py")
    make_pkg(str(tmp_path), "beta", BODY, filename="test_core.py")
    proc = run(str(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_build_dirs_are_skipped(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY)
    build = os.path.join(str(tmp_path), "beta", "build", "lib")
    os.makedirs(build)
    with open(os.path.join(str(tmp_path), "beta", "pyproject.toml"), "w") as fh:
        fh.write('[project]\nname = "beta"\n')
    with open(os.path.join(build, "core.py"), "w") as fh:
        fh.write(BODY)
    proc = run(str(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_json_output_shape(tmp_path):
    make_pkg(str(tmp_path), "alpha", BODY)
    make_pkg(str(tmp_path), "beta", BODY)
    proc = run(str(tmp_path), "--json")
    payload = json.loads(proc.stdout)
    assert proc.returncode == 1
    assert payload["packages"] == 2
    assert len(payload["duplicates"]) == 1
    assert payload["duplicates"][0]["packages"] == ["alpha", "beta"]


def test_missing_root_is_a_usage_error():
    proc = run()
    assert proc.returncode == 2


def test_no_packages_is_a_usage_error(tmp_path):
    proc = run(str(tmp_path))
    assert proc.returncode == 2
    assert "no packages" in proc.stderr
