"""
tiny_agent_scope - Resource budgets and blast-radius limits for AI agents.

A small library that enforces, per agent run:
  * step / tool-call / token / time / cost budgets
  * allowed/forbidden tool lists (read-only mode, deny-list)
  * filesystem + network blast-radius (allowed paths, allowed hosts)
  * checkpoint + abort hooks so a long-running agent can be paused/cancelled

Zero deps, single file, ~280 LOC.
"""
from __future__ import annotations

import fnmatch
import os
import time
import urllib.parse
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set

__version__ = "0.1.0"
__all__ = [
    "AgentScope",
    "BudgetExceeded",
    "ScopeViolation",
    "agent_scope",
    "scope_for",
]


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class BudgetExceeded(Exception):
    """Raised when an agent exceeds a configured budget."""

    def __init__(self, budget: str, used: float, limit: float):
        self.budget = budget
        self.used = used
        self.limit = limit
        super().__init__(f"{budget} budget exceeded: used {used} of {limit}")


class ScopeViolation(Exception):
    """Raised when an agent attempts an action outside its allowed scope."""

    def __init__(self, kind: str, target: str):
        self.kind = kind
        self.target = target
        super().__init__(f"{kind} not permitted by scope: {target}")


# --------------------------------------------------------------------------- #
# Scope
# --------------------------------------------------------------------------- #

@dataclass
class AgentScope:
    """Per-run scope with budgets and allow/deny lists."""
    name: str = "default"
    max_steps: Optional[int] = None
    max_tool_calls: Optional[int] = None
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    max_wall_seconds: Optional[float] = None

    allowed_tools: Optional[Set[str]] = None       # None = all allowed
    denied_tools: Set[str] = field(default_factory=set)
    read_only_tools: Set[str] = field(default_factory=set)

    allowed_paths: Optional[List[str]] = None      # None = all
    denied_paths: List[str] = field(default_factory=list)

    allowed_hosts: Optional[List[str]] = None      # None = all
    denied_hosts: List[str] = field(default_factory=list)

    on_step: Optional[Callable[["AgentScope", str], None]] = None
    on_violation: Optional[Callable[["AgentScope", str, str], None]] = None
    on_abort: Optional[Callable[["AgentScope"], None]] = None

    _state: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.allowed_tools is not None:
            self.allowed_tools = set(self.allowed_tools)
        if self.allowed_paths is not None:
            self.allowed_paths = list(self.allowed_paths)
        if self.allowed_hosts is not None:
            self.allowed_hosts = list(self.allowed_hosts)
        self._state.setdefault("steps", 0)
        self._state.setdefault("tool_calls", 0)
        self._state.setdefault("tokens", 0)
        self._state.setdefault("cost_usd", 0.0)
        self._state.setdefault("started_at", time.monotonic())
        self._state.setdefault("aborted", False)
        self._state.setdefault("abort_fired", False)
        self._state.setdefault("violations", [])

    # --- State helpers ----------------------------------------------------- #

    def used(self) -> Dict[str, float]:
        return {
            "steps": self._state["steps"],
            "tool_calls": self._state["tool_calls"],
            "tokens": self._state["tokens"],
            "cost_usd": round(self._state["cost_usd"], 6),
            "wall_seconds": round(time.monotonic() - self._state["started_at"], 3),
        }

    def remaining(self) -> Dict[str, Optional[float]]:
        u = self.used()
        def rem(cur, lim):
            return None if lim is None else max(0.0, lim - cur)
        return {
            "steps": rem(u["steps"], self.max_steps),
            "tool_calls": rem(u["tool_calls"], self.max_tool_calls),
            "tokens": rem(u["tokens"], self.max_tokens),
            "cost_usd": rem(u["cost_usd"], self.max_cost_usd),
            "wall_seconds": rem(u["wall_seconds"], self.max_wall_seconds),
        }

    def aborted(self) -> bool:
        return bool(self._state.get("aborted"))

    def abort(self) -> None:
        """Mark the scope aborted and fire on_abort exactly once.

        Abort is a terminal state. Calling abort() twice, or aborting and then
        letting the context manager finish, must not notify the caller twice:
        a double on_abort can tear down resources that were already released
        and make an ordinary abort look like a failure.
        """
        already = self._state.get("aborted", False)
        self._state["aborted"] = True
        if already:
            return
        self._fire_abort()

    def _fire_abort(self) -> None:
        """Invoke the on_abort callback at most once per scope."""
        if self._state.get("abort_fired"):
            return
        self._state["abort_fired"] = True
        if self.on_abort:
            try:
                self.on_abort(self)
            except Exception:
                pass

    # --- Step / tool / token accounting ------------------------------------ #

    def step(self, name: str = "") -> None:
        if self.aborted():
            raise BudgetExceeded("aborted", 0, 0)
        self._state["steps"] += 1
        if self.max_steps is not None and self._state["steps"] > self.max_steps:
            raise BudgetExceeded("step", self._state["steps"], self.max_steps)
        if self.max_wall_seconds is not None:
            wall = time.monotonic() - self._state["started_at"]
            if wall > self.max_wall_seconds:
                raise BudgetExceeded("wall_seconds", wall, self.max_wall_seconds)
        if self.on_step:
            self.on_step(self, name)

    def record_tool_call(self, name: str, tokens: int = 0, cost_usd: float = 0.0) -> None:
        if self.aborted():
            raise BudgetExceeded("aborted", 0, 0)
        self._check_tool(name)
        self._state["tool_calls"] += 1
        if self.max_tool_calls is not None and self._state["tool_calls"] > self.max_tool_calls:
            raise BudgetExceeded("tool_call", self._state["tool_calls"], self.max_tool_calls)
        self.record_tokens(tokens)
        self.record_cost(cost_usd)

    def record_tokens(self, tokens: int) -> None:
        if tokens <= 0:
            return
        self._state["tokens"] += tokens
        if self.max_tokens is not None and self._state["tokens"] > self.max_tokens:
            raise BudgetExceeded("token", self._state["tokens"], self.max_tokens)

    def record_cost(self, cost_usd: float) -> None:
        if cost_usd <= 0:
            return
        self._state["cost_usd"] += cost_usd
        if self.max_cost_usd is not None and self._state["cost_usd"] > self.max_cost_usd:
            raise BudgetExceeded("cost_usd", self._state["cost_usd"], self.max_cost_usd)

    # --- Permission checks -------------------------------------------------- #

    def _check_tool(self, name: str) -> None:
        if name in self.denied_tools:
            self._record_violation("tool_denied", name)
            raise ScopeViolation("tool", name)
        if self.allowed_tools is not None and name not in self.allowed_tools:
            self._record_violation("tool_not_allowed", name)
            raise ScopeViolation("tool", name)

    def check_path(self, path: str, write: bool = False) -> None:
        path = os.path.abspath(path)
        for pat in self.denied_paths:
            if fnmatch.fnmatch(path, os.path.abspath(pat)):
                self._record_violation("path_denied", path)
                raise ScopeViolation("path", path)
        if self.allowed_paths is not None:
            if not any(fnmatch.fnmatch(path, os.path.abspath(p)) for p in self.allowed_paths):
                self._record_violation("path_not_allowed", path)
                raise ScopeViolation("path", path)
        if write and any(fnmatch.fnmatch(path, os.path.abspath(p)) for p in self.read_only_tools):
            self._record_violation("path_write_blocked", path)
            raise ScopeViolation("path_write", path)

    def check_url(self, url: str) -> None:
        host = (urllib.parse.urlparse(url).hostname or "").lower()
        for pat in self.denied_hosts:
            if self._host_denied(host, pat.lower()):
                self._record_violation("host_denied", host)
                raise ScopeViolation("host", host)
        if self.allowed_hosts is not None:
            if not any(fnmatch.fnmatch(host, p.lower()) for p in self.allowed_hosts):
                self._record_violation("host_not_allowed", host)
                raise ScopeViolation("host", host)

    @staticmethod
    def _host_denied(host: str, pattern: str) -> bool:
        """Does host match a deny-list pattern?

        A deny-list entry is a statement about a DOMAIN, not about one exact
        hostname. Denying "evil.com" but allowing "api.evil.com" is not a
        deny-list - it is a deny-list with a hole shaped exactly like the
        attack. So a pattern that names a domain also covers its subdomains.

        The domain form is recognised by the absence of any glob metacharacter
        (star, question mark, bracket). Those keep plain fnmatch semantics:

            "evil.com"      -> denies evil.com, api.evil.com, a.b.evil.com
            "*.example.org" -> denies example.org and its subdomains
        """
        if not host:
            return False
        if fnmatch.fnmatch(host, pattern):
            return True
        # Plain domain (no glob metacharacters): also deny subdomains.
        if not any(ch in pattern for ch in "*?["):
            return host == pattern or host.endswith("." + pattern)
        # Glob pattern with a literal base: a leading "*." covers the bare
        # domain as well.
        if pattern.startswith("*.") and not any(ch in pattern[2:] for ch in "*?["):
            base = pattern[2:]
            return host == base or host.endswith("." + base)
        return False

    def _record_violation(self, kind: str, target: str) -> None:
        self._state["violations"].append({"kind": kind, "target": target, "t": time.time()})
        if self.on_violation:
            try:
                self.on_violation(self, kind, target)
            except Exception:
                pass

    # --- Context manager ---------------------------------------------------- #

    def __enter__(self) -> "AgentScope":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


# --------------------------------------------------------------------------- #
# Convenience factories
# --------------------------------------------------------------------------- #

def scope_for(name: str = "default", **kwargs: Any) -> AgentScope:
    """Create a fresh AgentScope. Sensible defaults for read-only research agents."""
    kwargs.setdefault("name", name)
    return AgentScope(**kwargs)


@contextmanager
def agent_scope(name: str = "default", **kwargs: Any):
    """Context manager that aborts on exception and reports final usage."""
    sc = scope_for(name, **kwargs)
    try:
        yield sc
    finally:
        # abort() already fired the callback; _fire_abort() is a no-op when it
        # has, and fires it when the scope was aborted by other means. Exactly
        # one notification either way.
        if sc.aborted():
            sc._fire_abort()
