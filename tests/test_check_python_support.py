"""Tests for scripts/check_python_support.py.

The checker has no tests of its own, which is how a bug in it went
unnoticed: it read only `python-version:` lines, so a workflow that
pinned its interpreter through a container image -- the only way to run
Python 3.7 on Actions now -- was reported as untested even though a
3.7 job existed and passed.

Each case below builds a throwaway package, so the tests exercise the
real parser rather than a description of it.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import textwrap

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, os.pardir, "scripts", "check_python_support.py")


def _load():
    spec = importlib.util.spec_from_file_location("check_python_support", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def checker():
    return _load()


def _make_package(tmp_path, workflow: str, floor: str = ">=3.8"):
    pkg = tmp_path / "pkg"
    (pkg / ".github" / "workflows").mkdir(parents=True)
    (pkg / "tiny_pkg.py").write_text("x = 1\n", encoding="utf-8")
    (pkg / "pyproject.toml").write_text(
        '[project]\nname = "tiny-pkg"\nversion = "0.1.0"\n'
        'requires-python = "%s"\n' % floor,
        encoding="utf-8",
    )
    (pkg / ".github" / "workflows" / "ci.yml").write_text(
        textwrap.dedent(workflow), encoding="utf-8"
    )
    return pkg


def test_matrix_versions_reads_setup_python_matrix(checker, tmp_path):
    pkg = _make_package(
        tmp_path,
        """
        name: CI
        on: [push]
        jobs:
          test:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                python-version: ["3.8", "3.9", "3.10"]
            steps:
              - uses: actions/setup-python@v5
                with:
                  python-version: ${{ matrix.python-version }}
        """,
    )
    versions, ok = checker.matrix_versions(str(pkg))
    assert ok
    assert (3, 8) in versions
    assert (3, 10) in versions


def test_matrix_versions_reads_container_image(checker, tmp_path):
    """A container-pinned interpreter is a tested interpreter.

    setup-python only ever published 3.7 for linux 20.04 and those runner
    images are retired, so the official python:3.7 container is the only
    way to execute 3.7 on Actions today.
    """
    pkg = _make_package(
        tmp_path,
        """
        name: CI
        on: [push]
        jobs:
          test-python37:
            runs-on: ubuntu-latest
            container: python:3.7
            steps:
              - uses: actions/checkout@v4
              - run: python -m pytest -q
        """,
    )
    versions, ok = checker.matrix_versions(str(pkg))
    assert ok
    assert (3, 7) in versions, "container image python:3.7 was not detected"


def test_matrix_versions_reads_container_with_tag_and_prefix(checker, tmp_path):
    pkg = _make_package(
        tmp_path,
        """
        name: CI
        on: [push]
        jobs:
          test:
            runs-on: ubuntu-latest
            container: python:3.9-slim
            steps:
              - run: python -m pytest -q
        """,
    )
    versions, ok = checker.matrix_versions(str(pkg))
    assert ok
    assert (3, 9) in versions


def test_no_workflow_is_not_ok(checker, tmp_path):
    pkg = _make_package(tmp_path, "name: CI\n")
    (pkg / ".github" / "workflows" / "ci.yml").unlink()
    versions, ok = checker.matrix_versions(str(pkg))
    assert versions == []
    assert not ok


def test_parse_floor(checker):
    assert checker.parse_floor(">=3.8") == (3, 8)
    assert checker.parse_floor(">=3.10") == (3, 10)
    assert checker.parse_floor(">=3.7") == (3, 7)
