"""Tests for scripts/scan_skills.py.

These are not coverage tests. Each one pins a behaviour the script would
silently lose if someone simplified it, and each is written so that it FAILS
against a weaker checker:

  test_version_drift_stops_the_scan          The whole point of the script.
                                              A stale baseline suppresses
                                              nothing, so every reviewed
                                              finding looks new. Only a
                                              version check can catch that,
                                              because neither the scanner nor
                                              a human reading a report can
                                              tell that a baseline went stale.

  test_uncovered_finding_fails_the_scan       A green build that accepts a
                                              new finding is worse than a
                                              red one: the baseline is a
                                              record of human review, and
                                              accepting an unreviewed finding
                                              discards that record silently.

  test_missing_baseline_fails_loudly          A missing baseline must not be
                                              read as "nothing to suppress".

  test_baseline_without_scanner_version_fails A baseline with no version key
                                              cannot be checked for drift, so
                                              it must fail rather than pass.

  test_scanner_version_is_read_from_stderr   The scanner prints its version
                                              to stderr on some installs.

  test_unrunnable_scanner_blames_the_python  The "requires a different
                                              Python" message reads like a
                                              missing interpreter if it is
                                              passed through verbatim.

  test_explicit_bin_beats_path                The script must not trust PATH
                                              alone: two installs can exist
                                              on one host, built against
                                              different Pythons.

  test_local_venv_beats_path                  The local install is the one
                                              that matches the baseline, so
                                              it must win over PATH.

Run: python3 -m pytest tests/ -q
"""

from __future__ import annotations

import importlib.util
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "scan_skills.py")

BASELINE_2132 = "version: 2\nscanner_version: 2.13.2\nrules: []\nfingerprints: []\n"


def load_script():
    """Import scripts/scan_skills.py as a module without running main()."""
    spec = importlib.util.spec_from_file_location("scan_skills", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FAKE_SCANNER = """#!{python}
import json
import sys

args = sys.argv[1:]

if args and args[0] == "--version":
    print({version_line}, file=sys.{version_stream})
    sys.exit({version_exit})

out = ""
for i, a in enumerate(args):
    if a == "--output" and i + 1 < len(args):
        out = args[i + 1]

if out:
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({payload}, fh)

sys.exit({scan_exit})
"""


def make_scanner(
    directory,
    version="2.13.2",
    issues=0,
    version_stream="stdout",
    version_exit=0,
    version_line=None,
    scan_exit=0,
    name="skillspector",
):
    """Write an executable stand-in for the skillspector binary."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    if version_line is None:
        version_line = "skillspector " + version

    payload = {
        "issues": [
            {
                "severity": "HIGH",
                "id": "E1",
                "location": {"file": "some-skill/SKILL.md", "start_line": 1},
            }
        ]
        * issues,
        "suppressed_count": 10,
        "risk_assessment": {"score": 0, "severity": "LOW"},
    }

    source = FAKE_SCANNER.format(
        python=sys.executable,
        version_line=repr(version_line),
        version_stream=version_stream,
        version_exit=version_exit,
        payload=repr(payload),
        scan_exit=scan_exit,
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    os.chmod(path, 0o755)
    return path


def prepare(tmp_path, monkeypatch, scanner, baseline_text=BASELINE_2132):
    """Point the script at a fake scanner and a controlled baseline."""
    mod = load_script()
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))
    baseline = os.path.join(str(tmp_path), ".skillspector-baseline.yaml")
    if baseline_text is not None:
        with open(baseline, "w", encoding="utf-8") as fh:
            fh.write(baseline_text)
    monkeypatch.setattr(mod, "BASELINE", baseline)
    monkeypatch.setattr(
        mod, "REPORT", os.path.join(str(tmp_path), ".skillspector-report.json")
    )
    monkeypatch.setenv("SKILLSPECTOR_BIN", scanner)
    return mod


def test_version_drift_stops_the_scan(tmp_path, monkeypatch, capsys):
    scanner = make_scanner(str(tmp_path), version="2.13.1")
    mod = prepare(tmp_path, monkeypatch, scanner)

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "does not match the baseline" in out
    assert "2.13.1" in out
    # The scan must not have run: if it had, the failure would be the
    # "not covered by the baseline" path and the drift would go unnoticed.
    assert "not covered by the baseline" not in out


def test_uncovered_finding_fails_the_scan(tmp_path, monkeypatch, capsys):
    scanner = make_scanner(str(tmp_path), version="2.13.2", issues=1)
    mod = prepare(tmp_path, monkeypatch, scanner)

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "not covered by the baseline" in out


def test_missing_baseline_fails_loudly(tmp_path, monkeypatch, capsys):
    scanner = make_scanner(str(tmp_path), version="2.13.2")
    mod = prepare(tmp_path, monkeypatch, scanner, baseline_text=None)

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "missing" in out


def test_baseline_without_scanner_version_fails(tmp_path, monkeypatch, capsys):
    scanner = make_scanner(str(tmp_path), version="2.13.2")
    mod = prepare(
        tmp_path, monkeypatch, scanner, baseline_text="version: 2\nrules: []\n"
    )

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "scanner_version" in out


def test_scanner_version_is_read_from_stderr(tmp_path, monkeypatch):
    scanner = make_scanner(str(tmp_path), version="2.13.2", version_stream="stderr")
    mod = prepare(tmp_path, monkeypatch, scanner)

    assert mod.scanner_version(scanner) == "2.13.2"


def test_unrunnable_scanner_blames_the_python(tmp_path, monkeypatch, capsys):
    scanner = make_scanner(
        str(tmp_path),
        version_exit=2,
        version_stream="stderr",
        version_line="skillspector requires a different Python",
    )
    mod = prepare(tmp_path, monkeypatch, scanner)

    with pytest.raises(SystemExit) as exc:
        mod.main()

    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert ">=3.12" in out
    assert "SKILLSPECTOR_BIN" in out


def test_explicit_bin_beats_path(tmp_path, monkeypatch):
    bindir = os.path.join(str(tmp_path), "bin")
    make_scanner(bindir, version="9.9.9")
    override = make_scanner(str(tmp_path), version="2.13.2", name="other-scanner")

    monkeypatch.setenv("PATH", bindir)
    monkeypatch.setenv("SKILLSPECTOR_BIN", override)
    mod = load_script()
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))

    assert mod.resolve_scanner() == override


def test_local_venv_beats_path(tmp_path, monkeypatch):
    bindir = os.path.join(str(tmp_path), "bin")
    make_scanner(bindir, version="9.9.9")
    venv_bin = os.path.join(str(tmp_path), ".venv", "bin")
    local = make_scanner(venv_bin, version="2.13.2")

    monkeypatch.setenv("PATH", bindir)
    monkeypatch.delenv("SKILLSPECTOR_BIN", raising=False)
    mod = load_script()
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))

    assert mod.resolve_scanner() == local
