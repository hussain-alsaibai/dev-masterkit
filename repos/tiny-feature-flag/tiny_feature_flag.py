"""
tiny-feature-flag - Zero-dependency feature flag / toggle evaluation.

A small library for evaluating feature flags at request time.  Flags are
defined as :class:`Flag` objects with a default state, a list of rules,
and a set of overrides.  Each rule is a callable that takes a
:class:`Context` and returns ``True``/``False`` (or a string for
percentage rollouts).

    from tiny_feature_flag import Flag, Rule, Context, FlagStore

    dark_mode = Flag(
        name="dark_mode",
        default=False,
        rules=[
            Rule.eq("user.plan", "pro"),
            Rule.in_("user.email", ["alice@x.com", "bob@x.com"]),
        ],
    )
    store = FlagStore({"dark_mode": dark_mode})

    if store.enabled("dark_mode", Context(user={"plan": "pro"})):
        ...

Why a feature flag library?  Hand-rolled flag checks grow into a
tangle of ``if user.plan == "pro" or user.email in [...]`` calls
that are hard to test, hard to audit, and hard to roll back.  A
flag definition is a single object: a name, a default, a list of
rules, and a list of overrides.  Evaluation is pure and synchronous.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union

__all__ = [
    "Flag",
    "FlagStore",
    "Context",
    "Rule",
    "FlagNotFound",
]
__version__ = "0.1.0"


class FlagNotFound(KeyError):
    """Raised when a flag is looked up by an unknown name."""


@dataclass
class Context:
    """Per-request evaluation context.

    Attributes can be accessed by path (``"user.plan"``) via :class:`Rule`
    helpers, or as a flat dict for custom rules.
    """

    user: Any = None
    request: Any = None
    env: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def get(self, path: str, default: Any = None) -> Any:
        """Look up a dotted path across ``user``, ``request``, ``env``, ``extra``.

        A path may be one of:
        - ``"user.X"`` -> ``self.user["X"]`` (or attribute).
        - ``"request.X"`` -> ``self.request["X"]``.
        - ``"env.X"`` -> ``self.env["X"]``.
        - ``"X"`` (no prefix) -> searched across all four in order.
        """
        if "." in path:
            head, rest = path.split(".", 1)
            src = {
                "user": self.user,
                "request": self.request,
                "env": self.env,
                "extra": self.extra,
            }.get(head, _MISSING)
            if src is _MISSING:
                return default
            value = _get_path(src, rest, _MISSING)
            return value if value is not _MISSING else default
        # No prefix: try each source with the bare key.
        for src in (self.user, self.request, self.env, self.extra):
            value = _get_path(src, path, _MISSING)
            if value is not _MISSING:
                return value
        return default


_MISSING = object()


def _get_path(obj: Any, path: str, default: Any) -> Any:
    if obj is None:
        return default
    if not path:
        return obj
    cur: Any = obj
    for part in path.split("."):
        if isinstance(cur, Mapping):
            if part not in cur:
                return default
            cur = cur[part]
        else:
            if not hasattr(cur, part):
                return default
            cur = getattr(cur, part)
    return cur


# ---------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------

RuleFunc = Callable[[Context], Optional[bool]]


class Rule:
    """Composable rule factories.  Each returns a callable.

    A rule is "matched" when the callable returns ``True``.  If it
    returns ``False`` the flag is forced off for this context.  If it
    returns ``None`` the next rule is tried.
    """

    @staticmethod
    def matches(predicate: Callable[[Any], bool], path: str, name: Optional[str] = None) -> RuleFunc:
        """``True`` when ``ctx.get(path)`` satisfies ``predicate``; otherwise defer.

        Use this when you want a tiered rollout (e.g. "pro users always,
        otherwise 20% of free users"). Use :meth:`eq` when you want a
        hard rule that forces the flag off on mismatch.
        """

        def _r(ctx: Context) -> Optional[bool]:
            value = ctx.get(path, _MISSING)
            if value is _MISSING:
                return None
            return True if predicate(value) else None

        _r.__name__ = name or f"matches({path})"
        return _r

    @staticmethod
    def eq(path: str, value: Any) -> RuleFunc:
        def _r(ctx: Context) -> Optional[bool]:
            v = ctx.get(path, _MISSING)
            if v is _MISSING:
                return None
            return v == value
        _r.__name__ = f"eq({path}={value!r})"
        return _r

    @staticmethod
    def ne(path: str, value: Any) -> RuleFunc:
        def _r(ctx: Context) -> Optional[bool]:
            v = ctx.get(path, _MISSING)
            if v is _MISSING:
                return None
            return v != value
        _r.__name__ = f"ne({path}!={value!r})"
        return _r

    @staticmethod
    def in_(path: str, values: Sequence[Any]) -> RuleFunc:
        s = set(values)
        def _r(ctx: Context) -> Optional[bool]:
            v = ctx.get(path, _MISSING)
            if v is _MISSING:
                return None
            return v in s
        _r.__name__ = f"in({path}, {list(values)!r})"
        return _r

    @staticmethod
    def contains(path: str, needle: Any) -> RuleFunc:
        def _r(ctx: Context) -> Optional[bool]:
            v = ctx.get(path, _MISSING)
            if v is _MISSING:
                return None
            try:
                return needle in v
            except TypeError:
                return False
        _r.__name__ = f"contains({path}, {needle!r})"
        return _r

    @staticmethod
    def predicate(fn: Callable[[Context], bool], name: Optional[str] = None) -> RuleFunc:
        """Wrap a plain ``Context -> bool`` function as a rule.

        Returning ``True`` enables the flag; ``False`` disables; ``None``
        defers to the next rule.
        """
        def _r(ctx: Context) -> Optional[bool]:
            return bool(fn(ctx)) or None  # None is treated as "no opinion"
        _r.__name__ = name or getattr(fn, "__name__", "predicate")
        return _r

    @staticmethod
    def percent(path: str, percent: int, *, salt: str = "") -> RuleFunc:
        """Stable percentage rollout keyed on ``path`` (default: ``user.id``).

        The same ``(value, salt)`` pair always lands in the same bucket.
        Returns ``True`` for the ``percent``% of values whose hash falls
        in ``[0, percent)`` and ``None`` for the rest (so the flag can
        still default off for non-matching contexts).
        """
        if not 0 <= percent <= 100:
            raise ValueError("percent must be in [0, 100]")

        def _r(ctx: Context) -> Optional[bool]:
            value = ctx.get(path, _MISSING)
            if value is _MISSING:
                return None
            bucket = _stable_bucket(str(value), salt)
            if bucket < percent:
                return True
            # Out of rollout bucket: defer to next rule (or default).
            return None
        _r.__name__ = f"percent({path}, {percent}%, salt={salt!r})"
        return _r


def _stable_bucket(value: str, salt: str) -> int:
    """Return a stable bucket in [0, 100) for ``value`` + ``salt``."""
    import hashlib
    h = hashlib.sha256((salt + "::" + value).encode("utf-8")).digest()
    # First 4 bytes interpreted big-endian, mod 100.
    n = int.from_bytes(h[:4], "big")
    return n % 100


# ---------------------------------------------------------------------------
# flag
# ---------------------------------------------------------------------------

@dataclass
class Flag:
    """A named feature flag.

    Evaluation order:
    1. ``overrides`` (forced True / forced False by name).
    2. ``rules`` (first rule returning a non-None bool wins).
    3. ``default`` (the fallback if no rule matched).
    """

    name: str
    default: bool = False
    rules: List[RuleFunc] = field(default_factory=list)
    description: str = ""
    # ``overrides`` maps a context path (``user.id``) to a forced bool.
    overrides: Dict[str, Dict[Any, bool]] = field(default_factory=dict)

    def evaluate(self, ctx: Context) -> bool:
        # 1. overrides
        for path, table in self.overrides.items():
            value = ctx.get(path, _MISSING)
            if value is not _MISSING and value in table:
                return table[value]
        # 2. rules
        for rule in self.rules:
            verdict = rule(ctx)
            if verdict is True:
                return True
            if verdict is False:
                return False
        # 3. default
        return self.default

    def add_override(self, path: str, value: Any, enabled: bool) -> None:
        self.overrides.setdefault(path, {})[value] = enabled


# ---------------------------------------------------------------------------
# store
# ---------------------------------------------------------------------------

class FlagStore:
    """A thread-safe registry of named flags.

    Lookup is by name; unknown names raise :class:`FlagNotFound`.
    """

    def __init__(self, flags: Optional[Mapping[str, Flag]] = None) -> None:
        self._lock = threading.RLock()
        self._flags: Dict[str, Flag] = {}
        if flags:
            for name, flag in flags.items():
                if not isinstance(flag, Flag):
                    raise TypeError(f"expected Flag, got {type(flag).__name__}")
                if flag.name != name:
                    raise ValueError(f"flag.name ({flag.name!r}) != key ({name!r})")
                self._flags[name] = flag

    def register(self, flag: Flag) -> None:
        with self._lock:
            if flag.name in self._flags:
                raise ValueError(f"flag {flag.name!r} already registered")
            self._flags[flag.name] = flag

    def unregister(self, name: str) -> None:
        with self._lock:
            self._flags.pop(name, None)

    def get(self, name: str) -> Flag:
        with self._lock:
            try:
                return self._flags[name]
            except KeyError as exc:
                raise FlagNotFound(f"unknown flag {name!r}; available: {sorted(self._flags)}") from exc

    def names(self) -> List[str]:
        with self._lock:
            return sorted(self._flags)

    def enabled(self, name: str, ctx: Optional[Context] = None) -> bool:
        return self.get(name).evaluate(ctx or Context())

    def evaluate_all(self, ctx: Optional[Context] = None) -> Dict[str, bool]:
        """Evaluate every flag in the store.  Useful for /debug/flags."""
        ctx = ctx or Context()
        with self._lock:
            items = list(self._flags.items())
        return {name: flag.evaluate(ctx) for name, flag in items}

