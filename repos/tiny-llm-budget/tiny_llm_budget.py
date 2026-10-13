"""tiny_llm_budget -- LLM context-window budget calculator (zero deps).

The smallest reliable way to know whether a prompt + completion will
fit a model's context window before you call the API. Pure Python,
zero dependencies, MIT licensed. ~150 LOC.

Why?
----
Calling a frontier model with a prompt that overflows the context
window either silently truncates (and you lose data) or hard-fails
(and you lose the call's cost). Most teams re-implement the
"count tokens" check per-service. tiny_llm_budget does it once:

    from tiny_llm_budget import plan

    plan("gpt-4o", system="You are ...", user=user_msg, expected_completion=800)

It returns a ``Budget`` dataclass with ``fits``, ``total_tokens``,
``remaining``, and a per-segment breakdown.

Token counting
--------------
Three strategies, in priority order:

1. ``tiktoken`` if installed. Drop-in accuracy for OpenAI models
   (``gpt-4o``, ``gpt-4o-mini``, ``gpt-4-turbo``, ``gpt-3.5-turbo``,
   ``o1-preview``, ``o1-mini``). Install with ``pip install tiktoken``.

2. Anthropic-style estimation if the model name starts with
   ``claude-``. Anthropic does not publish the BPE. We use a
   3.5-chars-per-token heuristic with a 1.1x safety multiplier
   (matches Anthropic's published "roughly 3.5 chars per token" plus
   a buffer for system overhead).

3. Generic heuristic. 4 chars per token for English text
   (research from Karpathy's minBPE + the OpenAI cookbook), with a
   1.15x safety multiplier. Good enough for budget planning, never
   good enough for billing.

Public API
----------
- :func:`count_tokens(text, model=...)` -- return an integer.
- :func:`plan(model, *, system='', user='', history=(), expected_completion=200, ...)`
  -- return a :class:`Budget`.
- :class:`Budget` -- dataclass result: ``fits``, ``total_tokens``,
  ``remaining``, ``max_tokens``, ``segments``, ``strategy``.
- :data:`MODEL_LIMITS` -- dict of ``model -> max context tokens``.
  Ships with the 2026-Q4 frontier set; pass a custom dict to extend.

Custom models
-------------
Pass ``model_limits={"my-fine-tune": 16384}`` to :func:`plan` for
fine-tunes or self-hosted endpoints. The lookup is case-insensitive.

Notes
-----
- "tokens" are tokenizer-aware for OpenAI; best-effort elsewhere.
  The output is a *budget* number, not a billing number. Always
  cross-check the API's reported ``usage.prompt_tokens`` for billing.
- History is a sequence of ``(role, text)`` pairs. Cost is symmetric
  in user/assistant roles.
- The function never raises on overflow; it returns ``fits=False``
  and a negative ``remaining``. Caller decides what to do.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence, Tuple


__version__ = "0.2.0"

__all__ = [
    "Budget",
    "COST_PER_MILLION",
    "MODEL_LIMITS",
    "Segment",
    "compare_models",
    "count_tokens",
    "plan",
    "register_model",
]


# ---------- Model context-window catalogue (2026-Q4) ----------

MODEL_LIMITS: dict = {
    # OpenAI
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-4": 8_192,
    "gpt-3.5-turbo": 16_385,
    "o1-preview": 128_000,
    "o1-mini": 128_000,
    # Anthropic
    "claude-3-5-sonnet": 200_000,
    "claude-3-5-haiku": 200_000,
    "claude-3-opus": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    # Google
    "gemini-1.5-pro": 1_000_000,
    "gemini-1.5-flash": 1_000_000,
    "gemini-2.0-flash-exp": 1_000_000,
    # Meta open-weights (hosted providers usually expose 8k-128k)
    "llama-3.1-405b": 128_000,
    "llama-3.1-70b": 128_000,
    "llama-3.1-8b": 128_000,
    # Mistral
    "mistral-large-2": 128_000,
    "mixtral-8x22b": 64_000,
    # DeepSeek
    "deepseek-v3": 64_000,
}


def register_model(name: str, max_tokens: int) -> None:
    """Add (or override) a model's context window size."""
    MODEL_LIMITS[name.lower()] = int(max_tokens)


# ---------- Token counting ----------


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in *text* for *model*. Zero-dep fallback if no
    tokenizer is available.

    Strategy:
      1. ``tiktoken`` for OpenAI models (exact).
      2. Anthropic heuristic for ``claude-*`` (3.5 chars/token, 1.1x
         safety multiplier).
      3. Generic heuristic for everyone else (4 chars/token, 1.15x
         safety multiplier).
    """
    if not text:
        return 0
    model_lc = (model or "").lower()
    if _is_openai_model(model_lc):
        try:
            import tiktoken  # type: ignore
            try:
                enc = tiktoken.encoding_for_model(model_lc)
            except KeyError:
                enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            pass
    if model_lc.startswith("claude-"):
        return _heuristic_count(text, chars_per_token=3.5, safety=1.1)
    return _heuristic_count(text, chars_per_token=4.0, safety=1.15)


def _is_openai_model(model_lc: str) -> bool:
    return any(
        model_lc.startswith(prefix)
        for prefix in ("gpt-", "o1-", "o3-", "o4-", "text-embedding-")
    )


def _heuristic_count(text: str, *, chars_per_token: float, safety: float) -> int:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    approx = len(cleaned) / chars_per_token
    return max(1, int(approx * safety + 0.5))


# ---------- Plan result ----------


@dataclass(frozen=True)
class Segment:
    """One slice of a budget plan."""
    name: str
    text: str
    tokens: int


@dataclass(frozen=True)
class Budget:
    """The result of :func:`plan`."""
    model: str
    max_tokens: int
    total_tokens: int
    remaining: int
    fits: bool
    segments: Tuple[Segment, ...] = field(default_factory=tuple)
    strategy: str = "heuristic"

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "total_tokens": self.total_tokens,
            "remaining": self.remaining,
            "fits": self.fits,
            "strategy": self.strategy,
            "segments": [
                {"name": s.name, "tokens": s.tokens} for s in self.segments
            ],
        }


# ---------- Plan computation ----------


HistoryLike = Sequence[Tuple[str, str]]


def plan(
    model: str,
    *,
    system: str = "",
    user: str = "",
    history: Optional[HistoryLike] = None,
    expected_completion: int = 0,
    tools_tokens: int = 0,
    safety_margin: float = 0.0,
    model_limits: Optional[Mapping[str, int]] = None,
) -> Budget:
    """Compute whether a prompt + expected completion fits *model*.

    Args:
      model: Model name; looked up in :data:`MODEL_LIMITS` (extend
        via ``model_limits=`` or :func:`register_model`).
      system: System prompt.
      user: Latest user message.
      history: Optional sequence of ``(role, text)`` pairs. Cost is
        summed symmetrically across roles.
      expected_completion: How many tokens you expect the model to
        produce. **Reserve this many tokens before you call.**
      tools_tokens: Pre-counted cost of tool/function definitions.
      safety_margin: Fractional headroom to keep free, e.g. ``0.05``
        for 5%.

    Returns:
      :class:`Budget` with ``fits`` boolean, ``total_tokens``,
      ``remaining`` (can be negative), and per-segment breakdown.
    """
    model_lc = (model or "").lower()
    limits = {k.lower(): v for k, v in MODEL_LIMITS.items()}
    if model_limits:
        for k, v in model_limits.items():
            limits[k.lower()] = int(v)
    max_tokens = limits.get(model_lc)
    if max_tokens is None:
        max_tokens = 8_192  # conservative default
    segments = []
    strategy = _strategy_for(model_lc)
    if system:
        segments.append(Segment("system", system, count_tokens(system, model_lc)))
    if history:
        for i, (role, text) in enumerate(history):
            segments.append(
                Segment(f"history[{i}].{role}", text, count_tokens(text, model_lc))
            )
    if user:
        segments.append(Segment("user", user, count_tokens(user, model_lc)))
    if tools_tokens:
        segments.append(Segment("tools", "", int(tools_tokens)))
    if expected_completion:
        segments.append(Segment("expected_completion", "", int(expected_completion)))
    raw_total = sum(s.tokens for s in segments)
    safety_tokens = int(raw_total * float(safety_margin))
    total = raw_total + safety_tokens
    remaining = max_tokens - total
    return Budget(
        model=model_lc,
        max_tokens=max_tokens,
        total_tokens=total,
        remaining=remaining,
        fits=remaining >= 0,
        segments=tuple(segments),
        strategy=strategy,
    )


def compare_models(
    models: Sequence[str],
    *,
    system: str = "",
    user: str = "",
    history: Optional[HistoryLike] = None,
    expected_completion: int = 0,
    tools_tokens: int = 0,
    safety_margin: float = 0.0,
    cost_per_million: Optional[Mapping[str, tuple]] = None,
    model_limits: Optional[Mapping[str, int]] = None,
) -> list:
    """Run :func:`plan` across multiple models and return sorted results.

    ``cost_per_million`` is an optional ``{model_name: (input_per_million, output_per_million)}``
    dict. If provided, the result includes an ``estimated_cost_usd`` field
    computed from the input tokens (system + history + user + tools) and
    the expected completion tokens at the model's published rates.

    Returns a list of ``(model, Budget, estimated_cost_usd_or_None)`` tuples
    sorted by ``fits`` first (descending), then ``remaining`` (descending),
    then ``estimated_cost_usd`` (ascending).
    """
    results = []
    for m in models:
        b = plan(
            m,
            system=system,
            user=user,
            history=history,
            expected_completion=expected_completion,
            tools_tokens=tools_tokens,
            safety_margin=safety_margin,
            model_limits=model_limits,
        )
        cost = _estimate_cost(b, cost_per_million) if cost_per_million else None
        results.append((m, b, cost))
    # Sort: fits first, then most remaining, then cheapest
    results.sort(key=lambda r: (not r[1].fits, -r[1].remaining, r[2] if r[2] is not None else float("inf")))
    return results


def _estimate_cost(budget, cost_per_million):
    """Return a float USD estimate for the budget, or None if rates unknown."""
    rates = cost_per_million.get(budget.model)
    if rates is None:
        return None
    in_rate, out_rate = rates  # USD per 1M tokens
    # Segments: system, history, user, tools = "input"; expected_completion = "output".
    input_tokens = 0
    output_tokens = 0
    for seg in budget.segments:
        if seg.name == "expected_completion":
            output_tokens += seg.tokens
        else:
            input_tokens += seg.tokens
    return round((input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate, 6)


# Default cost catalogue (USD per 1M tokens, input/output) for the 2026-Q4 set.
# Updated 2026-10-13.
COST_PER_MILLION = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "o1-preview": (15.00, 60.00),
    "o1-mini": (3.00, 12.00),
    # Anthropic
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-5-haiku": (0.80, 4.00),
    "claude-3-opus": (15.00, 75.00),
    "claude-3-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
    # Google
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-2.0-flash-exp": (0.0, 0.0),  # free during experimental
    # Meta / Llama (via Together / Fireworks, indicative)
    "llama-3.1-405b": (3.00, 3.00),
    "llama-3.1-70b": (0.88, 0.88),
    "llama-3.1-8b": (0.18, 0.18),
    # Mistral / DeepSeek
    "mistral-large-2": (2.00, 6.00),
    "mixtral-8x22b": (0.60, 0.60),
    "deepseek-v3": (0.27, 1.10),
}


def _strategy_for(model_lc: str) -> str:
    if _is_openai_model(model_lc):
        try:
            import tiktoken  # noqa: F401
            return "tiktoken"
        except ImportError:
            return "heuristic"
    if model_lc.startswith("claude-"):
        return "anthropic-heuristic"
    return "heuristic"
