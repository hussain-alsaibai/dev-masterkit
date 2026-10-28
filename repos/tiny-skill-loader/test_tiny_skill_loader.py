"""Tests for tiny_skill_loader - 26 tests."""
import os
import textwrap
import pytest
from pathlib import Path

from tiny_skill_loader import (
    Skill,
    SkillLoadError,
    SkillRegistry,
    discover_skills,
    load_skill_from_file,
    load_skill_from_dir,
)


# Manifest validation

def test_missing_required_key(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "x", "version": "0.1.0"}
        def register(reg, manifest): pass
    '''))
    with pytest.raises(SkillLoadError) as e:
        load_skill_from_file(str(f))
    assert "description" in str(e.value)


def test_invalid_name_chars(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "has space", "version": "0.1.0", "description": "x"}
    '''))
    with pytest.raises(SkillLoadError) as e:
        load_skill_from_file(str(f))
    assert "reserved" in str(e.value).lower()


def test_version_must_be_str(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "x", "version": 1, "description": "x"}
    '''))
    with pytest.raises(SkillLoadError):
        load_skill_from_file(str(f))


def test_tags_must_be_list(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "x", "version": "0.1.0", "description": "x", "tags": "nope"}
    '''))
    with pytest.raises(SkillLoadError):
        load_skill_from_file(str(f))


# File / path errors

def test_nonexistent_file(tmp_path):
    with pytest.raises(SkillLoadError):
        load_skill_from_file(str(tmp_path / "nope.py"))


def test_non_py_extension(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("MANIFEST = {}")
    with pytest.raises(SkillLoadError) as e:
        load_skill_from_file(str(f))
    assert ".py" in str(e.value)


def test_directory_loads(tmp_path):
    (tmp_path / "a.py").write_text(textwrap.dedent('''
        MANIFEST = {"name": "a", "version": "0.1.0", "description": "x"}
    '''))
    (tmp_path / "b.py").write_text(textwrap.dedent('''
        MANIFEST = {"name": "b", "version": "0.2.0", "description": "y"}
    '''))
    skills = load_skill_from_dir(str(tmp_path))
    names = {s.name for s in skills}
    assert names == {"a", "b"}


def test_underscore_files_skipped(tmp_path):
    (tmp_path / "_private.py").write_text("x = 1")
    (tmp_path / "real.py").write_text(textwrap.dedent('''
        MANIFEST = {"name": "real", "version": "0.1.0", "description": "x"}
    '''))
    skills = load_skill_from_dir(str(tmp_path))
    assert [s.name for s in skills] == ["real"]


# Register / tools / hooks

def test_register_with_decorators(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "s", "version": "0.1.0", "description": "x"}
        def register(reg, manifest):
            @reg.tool("ping")
            def ping(): return "pong"
            @reg.hook("startup")
            def startup(): return "started"
    '''))
    skill = load_skill_from_file(str(f))
    assert "ping" in skill.tools
    assert "startup" in skill.hooks
    assert skill.tools["ping"]() == "pong"


def test_register_with_explicit_calls(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "s", "version": "0.1.0", "description": "x"}
        def add(a, b): return a + b
        def register(reg, manifest):
            reg.tool("add", add)
    '''))
    skill = load_skill_from_file(str(f))
    assert skill.tools["add"](2, 3) == 5


def test_duplicate_tool_raises(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "s", "version": "0.1.0", "description": "x"}
        def register(reg, manifest):
            reg.tool("x", lambda: 1)
            reg.tool("x", lambda: 2)
    '''))
    with pytest.raises(SkillLoadError) as e:
        load_skill_from_file(str(f))
    assert "duplicate" in str(e.value).lower()


def test_no_register_ok(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "s", "version": "0.1.0", "description": "x"}
    '''))
    skill = load_skill_from_file(str(f))
    assert skill.tools == {}
    assert skill.hooks == {}


# Inference fallbacks

def test_manifest_only_register(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        def register(reg, manifest_only=True):
            return {"name": "s", "version": "0.1.0", "description": "x"}
    '''))
    skill = load_skill_from_file(str(f))
    assert skill.name == "s"


def test_legacy_register_no_args(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        def register(reg):
            reg.tool("legacy", lambda: "ok")
    '''))
    # MANIFEST-less but register has a usable docstring
    f.write_text(textwrap.dedent('''
        def register(reg):
            """Legacy skill registration."""
            reg.tool("legacy", lambda: "ok")
    '''))
    skill = load_skill_from_file(str(f))
    assert "legacy" in skill.tools


# Registry

def test_registry_register_and_get():
    sk = Skill(name="x", version="0.1.0", description="x")
    r = SkillRegistry()
    r.register_skill(sk)
    assert r.get("x") is sk


def test_registry_duplicate_rejected():
    sk = Skill(name="x", version="0.1.0", description="x")
    r = SkillRegistry()
    r.register_skill(sk)
    with pytest.raises(SkillLoadError):
        r.register_skill(sk)
    r.register_skill(sk, overwrite=True)


def test_registry_call_tool_routes_by_name(tmp_path):
    f = tmp_path / "s.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "s", "version": "0.1.0", "description": "x"}
        def register(reg, manifest):
            reg.tool("echo", lambda x: x)
    '''))
    sk = load_skill_from_file(str(f))
    r = SkillRegistry()
    r.register_skill(sk)
    assert r.call_tool("echo", x="hi") == "hi"


def test_registry_call_tool_missing():
    r = SkillRegistry()
    with pytest.raises(KeyError):
        r.call_tool("missing")


def test_registry_fire_hook_calls_all():
    r = SkillRegistry()
    s1 = Skill(name="a", version="0.1.0", description="x")
    s1.hooks["startup"] = lambda: "a"
    s2 = Skill(name="b", version="0.1.0", description="x")
    s2.hooks["startup"] = lambda: "b"
    r.register_skill(s1)
    r.register_skill(s2)
    out = r.fire_hook("startup")
    assert sorted(out) == ["a", "b"]


def test_registry_unregister():
    r = SkillRegistry()
    r.register_skill(Skill(name="x", version="0.1.0", description="x"))
    r.unregister("x")
    assert r.get("x") is None
    r.unregister("x")  # idempotent


def test_registry_list_tools_namespaced():
    r = SkillRegistry()
    s1 = Skill(name="jira", version="0.1.0", description="x")
    s1.tools["search"] = lambda: None
    s2 = Skill(name="git", version="0.1.0", description="x")
    s2.tools["status"] = lambda: None
    r.register_skill(s1)
    r.register_skill(s2)
    assert r.list_tools() == ["git.status", "jira.search"]


# Discovery

def test_discover_mixed_paths(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "x.py").write_text(textwrap.dedent('''
        MANIFEST = {"name": "x", "version": "0.1.0", "description": "x"}
    '''))
    f = tmp_path / "y.py"
    f.write_text(textwrap.dedent('''
        MANIFEST = {"name": "y", "version": "0.1.0", "description": "y"}
    '''))
    skills = discover_skills([str(d), str(f)])
    names = {s.name for s in skills}
    assert names == {"x", "y"}


def test_discover_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.py").write_text(textwrap.dedent('''
        MANIFEST = {"name": "deep", "version": "0.1.0", "description": "x"}
    '''))
    skills = discover_skills([str(tmp_path)], recursive=True)
    assert any(s.name == "deep" for s in skills)


def test_skill_to_dict():
    sk = Skill(name="x", version="0.1.0", description="desc", tags=["a"])
    sk.tools["t"] = lambda: None
    d = sk.to_dict()
    assert d["name"] == "x"
    assert d["tools"] == ["t"]
    assert "loaded_at" in d


def test_syntax_error_in_skill(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("def register(reg, manifest\n")
    with pytest.raises(SkillLoadError):
        load_skill_from_file(str(f))


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
