"""Tests for scripts/check_version_drift.py.

Each test below was written against a real defect measured on 2026-11-05, and
each one is written so that it FAILS against a weaker checker:

  test_stale_package_json_is_reported   snapshot of snapdb's real drift
                                        (package.json 0.11.0 vs pyproject 0.18.0,
                                        seven minor releases, guard passing)
  test_single_surface_is_not_a_finding  a repo that states its version once
                                        cannot drift; flagging it is noise
  test_prerelease_tail_is_not_drift     `1.0.0-rc1` on one surface and
                                        `1.0.0` on another is drift; `-rc1`
                                        against `-rc1` is not. A normaliser
                                        that strips the tail hides both cases.
  test_poetry_table_is_read            a repo that still uses [tool.poetry]

Run: python3 -m pytest tests/ -q
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "scripts", "check_version_drift.py")


def run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True,
        text=True,
    )


def make_repo(root, name, pyproject=None, package_json=None, dunder=None):
    repo = os.path.join(root, name)
    os.makedirs(repo, exist_ok=True)
    if pyproject is not None:
        with open(os.path.join(repo, "pyproject.toml"), "w") as fh:
            fh.write(pyproject)
    if package_json is not None:
        with open(os.path.join(repo, "package.json"), "w") as fh:
            json.dump(package_json, fh)
    if dunder is not None:
        pkg = os.path.join(repo, name.replace("-", "_"))
        os.makedirs(pkg, exist_ok=True)
        with open(os.path.join(pkg, "__init__.py"), "w") as fh:
            fh.write('__version__ = "%s"\n' % dunder)
    return repo


def pyproject(version):
    return '[project]\nname = "thing"\nversion = "%s"\n' % version


def package_json(version):
    return {"name": "thing", "version": version}


def inspect_json(path):
    result = run("--repo", path, "--json")
    assert result.returncode in (0, 1), result.stderr
    return json.loads(result.stdout)[0]


# --- the defect that motivated the script (snapdb, 2026-11-05) -------------

def test_stale_package_json_is_reported(tmp_path):
    repo = make_repo(
        str(tmp_path), "snapdb",
        pyproject=pyproject("0.18.0"),
        package_json=package_json("0.11.0"),
        dunder="0.18.0",
    )
    result = run("--repo", repo)
    assert result.returncode == 1, result.stdout
    assert "DRIFT" in result.stdout
    assert "0.11.0" in result.stdout and "0.18.0" in result.stdout


def test_two_of_three_agreeing_is_still_drift(tmp_path):
    """The guard that existed passed 4 tests; the third surface was stale."""
    repo = make_repo(
        str(tmp_path), "snapdb",
        pyproject=pyproject("0.18.0"),
        package_json=package_json("0.11.0"),
        dunder="0.18.0",
    )
    item = inspect_json(repo)
    assert item["stale"] is True
    versions = sorted(s["normalised"] for s in item["surfaces"])
    assert versions == ["0.11.0", "0.18.0", "0.18.0"]


# --- the noise the script must not emit -----------------------------------

def test_single_surface_is_not_a_finding(tmp_path):
    repo = make_repo(str(tmp_path), "solo", package_json=package_json("1.2.3"))
    result = run("--repo", repo)
    assert result.returncode == 0, result.stdout
    assert "DRIFT" not in result.stdout
    assert "1 " in result.stdout  # still inspected, not silently skipped


def test_agreeing_surfaces_are_ok(tmp_path):
    repo = make_repo(
        str(tmp_path), "agree",
        pyproject=pyproject("2.0.0"),
        package_json=package_json("2.0.0"),
        dunder="2.0.0",
    )
    result = run("--repo", repo)
    assert result.returncode == 0, result.stdout
    assert "ok" in result.stdout


def test_missing_package_json_is_not_drift(tmp_path):
    repo = make_repo(str(tmp_path), "pyonly", pyproject=pyproject("1.0.0"),
                     dunder="1.0.0")
    assert run("--repo", repo).returncode == 0


# --- version-shape handling ----------------------------------------------

def test_prerelease_tail_does_not_create_drift(tmp_path):
    repo = make_repo(
        str(tmp_path), "pre",
        pyproject=pyproject("1.0.0-rc1"),
        package_json=package_json("1.0.0-rc1"),
    )
    assert run("--repo", repo).returncode == 0


def test_prerelease_versus_release_is_drift(tmp_path):
    """A normaliser that strips every tail would call these equal."""
    repo = make_repo(
        str(tmp_path), "pre2",
        pyproject=pyproject("1.0.0"),
        package_json=package_json("1.0.0-rc1"),
    )
    assert run("--repo", repo).returncode == 1


def test_leading_v_is_not_drift(tmp_path):
    repo = make_repo(
        str(tmp_path), "vtag",
        pyproject=pyproject("1.4.2"),
        package_json=package_json("v1.4.2"),
    )
    assert run("--repo", repo).returncode == 0


def test_two_component_version_matches_three(tmp_path):
    repo = make_repo(
        str(tmp_path), "short",
        pyproject=pyproject("1.4"),
        package_json=package_json("1.4.0"),
    )
    assert run("--repo", repo).returncode == 0


# --- pyproject dialect ----------------------------------------------------

def test_poetry_table_is_read(tmp_path):
    repo = make_repo(
        str(tmp_path), "poetry",
        pyproject='[tool.poetry]\nname = "thing"\nversion = "0.3.0"\n',
        package_json=package_json("0.2.0"),
    )
    result = run("--repo", repo)
    assert result.returncode == 1, result.stdout
    assert "[tool.poetry]" in result.stdout


def test_dynamic_version_is_skipped_not_guessed(tmp_path):
    """`dynamic = ["version"]` is indirection, not a stated version."""
    repo = make_repo(
        str(tmp_path), "dyn",
        pyproject='[project]\nname = "thing"\ndynamic = ["version"]\n',
        package_json=package_json("9.9.9"),
    )
    result = run("--repo", repo)
    assert result.returncode == 0, result.stdout
    assert "DRIFT" not in result.stdout


# --- directory walk -------------------------------------------------------

def test_root_walk_finds_only_repo_shaped_dirs(tmp_path):
    make_repo(str(tmp_path), "one", pyproject=pyproject("1.0.0"))
    make_repo(str(tmp_path), "two", pyproject=pyproject("2.0.0"),
              package_json=package_json("1.0.0"))
    os.makedirs(os.path.join(str(tmp_path), "notes"), exist_ok=True)
    with open(os.path.join(str(tmp_path), "notes", "x.md"), "w") as fh:
        fh.write("no manifest here\n")

    result = run("--root", str(tmp_path))
    assert result.returncode == 1, result.stdout
    assert "two" in result.stdout
    assert "notes" not in result.stdout
    assert "DRIFT  one" not in result.stdout


def test_no_repos_is_a_usage_error(tmp_path):
    os.makedirs(os.path.join(str(tmp_path), "empty"), exist_ok=True)
    result = run("--root", str(tmp_path))
    assert result.returncode == 2
    assert "no stated versions" in result.stderr


def test_missing_root_is_a_usage_error(tmp_path):
    result = run("--root", os.path.join(str(tmp_path), "nope"))
    assert result.returncode == 2
