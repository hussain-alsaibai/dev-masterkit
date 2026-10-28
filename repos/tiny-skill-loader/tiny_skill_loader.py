"""
tiny_skill_loader - Runtime skill/extension loader for AI agents.

Discovers and loads "skill" plugins (single-file Python modules exposing
a `register()` function or a top-level SKILL.md-style manifest). Validates
manifests, mounts them into a shared registry, and exposes them to the
agent's tool-call layer. Zero deps, single file, ~260 LOC.
"""
from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

__version__ = "0.1.0"
__all__ = [
    "Skill",
    "SkillLoadError",
    "SkillRegistry",
    "discover_skills",
    "load_skill_from_file",
    "load_skill_from_dir",
]

REQUIRED_MANIFEST_KEYS = ("name", "version", "description")
RESERVED_NAME_CHARS = set("/\\ \t\n")


class SkillLoadError(Exception):
    """Raised when a skill fails to load or validate."""


@dataclass
class Skill:
    """A loaded skill with its manifest metadata and tool surface."""
    name: str
    version: str
    description: str
    path: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    tools: Dict[str, Callable[..., Any]] = field(default_factory=dict)
    hooks: Dict[str, Callable[..., Any]] = field(default_factory=dict)
    module: Any = None
    loaded_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "path": self.path,
            "author": self.author,
            "tags": list(self.tags),
            "requires": list(self.requires),
            "tools": sorted(self.tools.keys()),
            "hooks": sorted(self.hooks.keys()),
            "loaded_at": self.loaded_at,
        }


def _validate_manifest(name, manifest, path):
    for k in REQUIRED_MANIFEST_KEYS:
        if k not in manifest:
            raise SkillLoadError(f"skill {name!r} manifest missing required key: {k}")
    if not isinstance(manifest["name"], str) or not manifest["name"]:
        raise SkillLoadError("skill manifest has invalid name")
    if any(c in RESERVED_NAME_CHARS for c in manifest["name"]):
        raise SkillLoadError(f"skill name has reserved chars: {manifest['name']!r}")
    if not isinstance(manifest["version"], str):
        raise SkillLoadError(f"skill {name!r} version must be a string")
    if not isinstance(manifest["description"], str):
        raise SkillLoadError(f"skill {name!r} description must be a string")
    for k in ("tags", "requires"):
        if k in manifest and not isinstance(manifest[k], list):
            raise SkillLoadError(f"skill {name!r} {k} must be a list")


def _import_module_from_path(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise SkillLoadError(f"could not build module spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        sys.modules.pop(module_name, None)
        raise SkillLoadError(f"error executing {path}: {e}") from e
    return mod


def _accepts_manifest_only(sig) -> bool:
    """Does this signature accept manifest_only=True?

    True when the parameter exists at all, or when it exists via **kwargs
    (a wrapper function that forwards arguments cannot be introspected any
    further, and guessing wrong here means a skill never gets asked for its
    manifest).
    """
    try:
        params = sig.parameters
    except (TypeError, ValueError):
        return False
    if "manifest_only" in params:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


def _extract_manifest(mod, path):
    if hasattr(mod, "MANIFEST"):
        manifest = mod.MANIFEST
        if not isinstance(manifest, dict):
            raise SkillLoadError(f"{path}: MANIFEST must be a dict")
        return manifest
    if hasattr(mod, "manifest"):
        manifest = mod.manifest
        if isinstance(manifest, dict):
            return manifest
    if hasattr(mod, "register"):
        fn = mod.register
        sig = inspect.signature(fn)
        # A register() that accepts manifest_only is declaring: "call me with
        # manifest_only=True and I will hand back the manifest dict". That
        # signal stands on its own. The old code only called it when the
        # signature ALSO declared a "manifest" parameter, so a skill written
        # as register(reg, manifest_only=True) was never asked and the loader
        # fell back to a synthetic name derived from the module hash.
        if _accepts_manifest_only(sig):
            # The documented manifest-only form is register(reg, manifest_only=True):
            # the registry is still passed positionally, the flag just tells the
            # skill not to register tools and to hand the manifest back instead.
            # So the call needs a registry argument. A throwaway one is fine
            # here - the real registry is used later, in _call_register.
            probe = SkillRegistry()
            result = None
            for call in (
                lambda: fn(probe, manifest_only=True),
                lambda: fn(manifest_only=True),
            ):
                try:
                    result = call()
                    break
                except TypeError:
                    continue
            if isinstance(result, dict):
                return result
        return {
            "name": getattr(mod, "__name__", Path(path).stem),
            "version": getattr(mod, "__version__", "0.0.0"),
            "description": (inspect.getdoc(fn) or "").strip().split("\n")[0] or "(no description)",
        }
    raise SkillLoadError(f"{path}: no MANIFEST, manifest dict, or register() found")


def _call_register(mod, registry, manifest):
    if not hasattr(mod, "register"):
        return
    fn = mod.register
    sig = inspect.signature(fn)
    if _accepts_manifest_only(sig):
        try:
            fn(registry, manifest_only=True)
            return
        except TypeError:
            pass
    try:
        fn(registry, manifest)
    except TypeError:
        try:
            fn(registry)
        except TypeError:
            fn()


def load_skill_from_file(path):
    p = Path(path)
    if not p.is_file():
        raise SkillLoadError(f"not a file: {path}")
    if p.suffix != ".py":
        raise SkillLoadError(f"skill file must end in .py: {path}")
    mod_name = f"_tiny_skill_{p.stem}_{abs(hash(str(p.resolve())))}"
    mod = _import_module_from_path(str(p), mod_name)
    manifest = _extract_manifest(mod, str(p))
    _validate_manifest(manifest.get("name", p.stem), manifest, str(p))
    skill = Skill(
        name=manifest["name"],
        version=manifest["version"],
        description=manifest["description"],
        path=str(p),
        author=manifest.get("author"),
        tags=list(manifest.get("tags", [])),
        requires=list(manifest.get("requires", [])),
        module=mod,
    )
    registry = SkillRegistry(_building=skill)
    _call_register(mod, registry, manifest)
    skill.tools = dict(registry._tools_pending)
    skill.hooks = dict(registry._hooks_pending)
    return skill


def load_skill_from_dir(directory):
    p = Path(directory)
    if not p.is_dir():
        raise SkillLoadError(f"not a directory: {directory}")
    out = []
    for f in sorted(p.glob("*.py")):
        if f.name.startswith("_"):
            continue
        out.append(load_skill_from_file(str(f)))
    return out


def discover_skills(paths, recursive=True):
    """Discover and load skills from a list of directory paths."""
    out = []
    for base in paths:
        p = Path(base)
        if p.is_file() and p.suffix == ".py":
            out.append(load_skill_from_file(str(p)))
        elif p.is_dir():
            glob = "**/*.py" if recursive else "*.py"
            for f in sorted(p.glob(glob)):
                if f.name.startswith("_"):
                    continue
                out.append(load_skill_from_file(str(f)))
    return out


class SkillRegistry:
    """A registry the agent tool-call layer queries for skill-provided tools."""

    def __init__(self, _building=None):
        self._building = _building
        self._tools_pending = {}
        self._hooks_pending = {}
        self._loaded = {}

    def tool(self, name, fn=None):
        if fn is not None:
            if name in self._tools_pending:
                raise SkillLoadError(f"duplicate tool: {name}")
            self._tools_pending[name] = fn
            return fn
        def deco(f):
            self.tool(name, f)
            return f
        return deco

    def hook(self, name, fn=None):
        if fn is not None:
            if name in self._hooks_pending:
                raise SkillLoadError(f"duplicate hook: {name}")
            self._hooks_pending[name] = fn
            return fn
        def deco(f):
            self.hook(name, f)
            return f
        return deco

    def manifest(self):
        if self._building is None:
            return {}
        return {
            "name": self._building.name,
            "version": self._building.version,
            "tools": sorted(self._tools_pending.keys()),
            "hooks": sorted(self._hooks_pending.keys()),
        }

    def register_skill(self, skill, overwrite=False):
        if skill.name in self._loaded and not overwrite:
            raise SkillLoadError(f"skill already loaded: {skill.name}")
        self._loaded[skill.name] = skill

    def unregister(self, name):
        self._loaded.pop(name, None)

    def get(self, name):
        return self._loaded.get(name)

    def call_tool(self, name, *args, **kwargs):
        for skill in self._loaded.values():
            if name in skill.tools:
                return skill.tools[name](*args, **kwargs)
        raise KeyError(f"no skill provides tool: {name}")

    def fire_hook(self, name, *args, **kwargs):
        results = []
        for skill in self._loaded.values():
            if name in skill.hooks:
                results.append(skill.hooks[name](*args, **kwargs))
        return results

    def list_skills(self):
        return [s.to_dict() for s in self._loaded.values()]

    def list_tools(self):
        """Namespaced tool names, sorted.

        Sorted, not insertion-ordered: the caller is an agent that is handed
        this list to choose from, and a stable order means the same tool
        surface always reads the same way regardless of the order skills
        happened to be registered in.
        """
        out = []
        for s in self._loaded.values():
            out.extend(f"{s.name}.{t}" for t in s.tools)
        return sorted(out)
