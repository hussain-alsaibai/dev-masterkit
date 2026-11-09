"""Tests for scripts/ecosystem_smoke.py.

These are not coverage tests. Each one pins a behaviour that the script would
silently lose if someone simplified it:

`test_empty_wheel_is_rejected` is the reason the script inspects the wheel
instead of trusting the build's exit code -- setuptools builds a wheel
containing only dist-info without complaint, and that wheel installs cleanly
and then raises ModuleNotFoundError. `test_readme_warning_suppresses_finding`
is the reason the README check looks for *any* warning, not one exact
sentence: three READMEs already say it three different ways, and a strict
match would report all three as defects. `test_pip_install_line_fires_only_
when_name_is_taken` is the reason the check is keyed on PyPI ownership rather
than on the presence of the line -- most of these packages are unpublished,
and an unpublished name is not a collision.

Run: python3 -m pytest tests/ -q
"""

from __future__ import annotations

import os
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import ecosystem_smoke as es  # noqa: E402


def _wheel(path: str, names) -> str:
    with zipfile.ZipFile(path, "w") as zf:
        for name in names:
            zf.writestr(name, "")
    return path


# ---------- module name mapping ----------


def test_module_name_replaces_hyphens():
    assert es.module_name("tiny-queue") == "tiny_queue"


def test_module_name_honours_overrides():
    # fast-cache ships fast_cache.py, not fast_cache as a package; the
    # hyphen rule happens to be right here, but the override table is what
    # keeps a package like tiny-mcp-skel honest.
    assert es.module_name("tiny-mcp-skel") == "tiny_mcp_skel"


# ---------- the empty-wheel trap ----------


def test_empty_wheel_is_rejected(tmp_path):
    wheel = _wheel(
        str(tmp_path / "e.whl"),
        ["tiny_x-0.1.0.dist-info/METADATA", "tiny_x-0.1.0.dist-info/RECORD"],
    )
    ok, names = es.wheel_ships_module(wheel, "tiny_x")
    assert ok is False
    assert any("dist-info" in n for n in names)


def test_wheel_with_module_is_accepted(tmp_path):
    wheel = _wheel(
        str(tmp_path / "g.whl"),
        ["tiny_x.py", "tiny_x-0.1.0.dist-info/METADATA"],
    )
    ok, _ = es.wheel_ships_module(wheel, "tiny_x")
    assert ok is True


def test_wheel_with_package_dir_is_accepted(tmp_path):
    wheel = _wheel(
        str(tmp_path / "p.whl"),
        ["tiny_x/__init__.py", "tiny_x-0.1.0.dist-info/METADATA"],
    )
    ok, _ = es.wheel_ships_module(wheel, "tiny_x")
    assert ok is True


# ---------- packaging presence ----------


def test_has_packaging_accepts_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    assert es.has_packaging(str(tmp_path)) is True


def test_has_packaging_accepts_setup_py(tmp_path):
    (tmp_path / "setup.py").write_text("from setuptools import setup\n")
    assert es.has_packaging(str(tmp_path)) is True


def test_has_packaging_rejects_bare_module(tmp_path):
    (tmp_path / "tiny_x.py").write_text("x = 1\n")
    (tmp_path / "test_tiny_x.py").write_text("")
    assert es.has_packaging(str(tmp_path)) is False


# ---------- README squat detection ----------


def _readme(tmp_path, pkg, body):
    d = tmp_path / "repos" / pkg
    d.mkdir(parents=True)
    (d / "README.md").write_text(body)
    return str(tmp_path)


def test_pip_install_line_fires_only_when_name_is_taken(tmp_path):
    root = _readme(tmp_path, "tiny-queue", "```bash\npip install tiny-queue\n```\n")
    findings = es.readme_install_lines("tiny-queue", root, {"tiny-queue": "Someone Else"})
    assert [f.code for f in findings] == ["SQUAT-CMD"]


def test_pip_install_line_is_silent_when_name_is_free(tmp_path):
    root = _readme(tmp_path, "tiny-queue", "```bash\npip install tiny-queue\n```\n")
    findings = es.readme_install_lines("tiny-queue", root, {"tiny-queue": None})
    assert findings == []


@pytest.mark.parametrize(
    "warning",
    [
        "> Do not run `pip install tiny-queue`; that name is taken.",
        "The name `tiny-queue` on PyPI belongs to a different project.",
        "That name belongs to a different project, so use the git URL.",
        "installing `pip install tiny-queue` would fetch that package instead",
    ],
)
def test_readme_warning_suppresses_finding(tmp_path, warning):
    # Different READMEs state the warning differently. A single-phrase match
    # would report three healthy repos as broken.
    body = f"```bash\npip install tiny-queue\n```\n\n{warning}\n"
    root = _readme(tmp_path, "tiny-queue", body)
    findings = es.readme_install_lines("tiny-queue", root, {"tiny-queue": "Someone Else"})
    assert findings == []


def test_missing_readme_is_not_a_crash(tmp_path):
    findings = es.readme_install_lines("tiny-queue", str(tmp_path), {"tiny-queue": "X"})
    assert findings == []


# ---------- offline mode ----------


def test_offline_clone_check_reports_missing_packaging(tmp_path):
    d = tmp_path / "repos" / "tiny-rate"
    d.mkdir(parents=True)
    (d / "tiny_rate.py").write_text("x = 1\n")
    findings = es.check_local_clone("tiny-rate", str(tmp_path))
    assert [f.code for f in findings] == ["NO-PACKAGING"]
    assert findings[0].level == "FAIL"


def test_offline_clone_check_passes_a_packaged_repo(tmp_path):
    d = tmp_path / "repos" / "tiny-queue"
    d.mkdir(parents=True)
    (d / "pyproject.toml").write_text("[project]\n")
    (d / "tiny_queue.py").write_text("x = 1\n")
    findings = es.check_local_clone("tiny-queue", str(tmp_path))
    assert [f.code for f in findings] == ["PACKAGED"]
    assert findings[0].level == "ok"


def test_offline_clone_check_flags_metadata_without_module(tmp_path):
    d = tmp_path / "repos" / "tiny-queue"
    d.mkdir(parents=True)
    (d / "pyproject.toml").write_text("[project]\n")
    (d / "tiny_queu.py").write_text("typo\n")
    findings = es.check_local_clone("tiny-queue", str(tmp_path))
    assert [f.code for f in findings] == ["NO-MODULE"]


# ---------- manifest contract ----------


def test_default_manifest_has_no_duplicates():
    assert len(es.DEFAULT_MANIFEST) == len(set(es.DEFAULT_MANIFEST))


def test_only_rejects_an_unknown_package(tmp_path):
    rc = es.main(["--offline", "--only", "tiny-not-real", "--root", str(tmp_path)])
    assert rc == 2
