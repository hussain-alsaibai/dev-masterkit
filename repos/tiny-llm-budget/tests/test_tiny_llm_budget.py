"""Tests for tiny_llm_budget."""

from __future__ import annotations

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tiny_llm_budget import (  # noqa: E402
    Budget,
    MODEL_LIMITS,
    Segment,
    count_tokens,
    plan,
    register_model,
)


class TestCountTokens(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(count_tokens(""), 0)
        self.assertEqual(count_tokens("", "gpt-4o"), 0)

    def test_heuristic_grows_with_length(self) -> None:
        a = count_tokens("hello world", "llama-3.1-70b")
        b = count_tokens("hello world " * 100, "llama-3.1-70b")
        self.assertGreater(b, a * 50)

    def test_anthropic_uses_3_5_charset(self) -> None:
        # 100 chars at 3.5 chars/token + 1.1x safety = ~32 tokens
        n = count_tokens("a" * 100, "claude-3-5-sonnet")
        self.assertGreaterEqual(n, 28)
        self.assertLessEqual(n, 38)

    def test_strips_control_chars(self) -> None:
        # Control characters should not be charged
        n_clean = count_tokens("hello world", "llama-3.1-70b")
        n_dirty = count_tokens("hello\x00\x01world", "llama-3.1-70b")
        self.assertEqual(n_clean, n_dirty)

    def test_min_one_token(self) -> None:
        # Even a single character counts as 1 token
        self.assertEqual(count_tokens("a", "llama-3.1-70b"), 1)


class TestModelLimits(unittest.TestCase):
    def test_known_models(self) -> None:
        self.assertEqual(MODEL_LIMITS["gpt-4o"], 128_000)
        self.assertEqual(MODEL_LIMITS["claude-3-5-sonnet"], 200_000)
        self.assertEqual(MODEL_LIMITS["gemini-1.5-pro"], 1_000_000)

    def test_register_model(self) -> None:
        register_model("my-fine-tune", 16384)
        self.assertEqual(MODEL_LIMITS["my-fine-tune"], 16384)
        # Cleanup
        del MODEL_LIMITS["my-fine-tune"]


class TestPlan(unittest.TestCase):
    def test_simple_prompt_fits(self) -> None:
        b = plan("gpt-4o", system="You are a helper.", user="hi")
        self.assertTrue(b.fits)
        self.assertGreater(b.max_tokens, 0)
        self.assertEqual(b.model, "gpt-4o")
        self.assertEqual(len(b.segments), 2)

    def test_segments_have_names(self) -> None:
        b = plan(
            "gpt-4o",
            system="sys",
            user="usr",
            history=[("user", "q1"), ("assistant", "a1")],
            expected_completion=100,
        )
        names = [s.name for s in b.segments]
        self.assertEqual(
            names,
            ["system", "history[0].user", "history[1].assistant", "user", "expected_completion"],
        )

    def test_overflow_returns_fits_false(self) -> None:
        # 4k model, push way more than that
        b = plan(
            "gpt-4",
            system="x" * 50_000,
            user="hi",
        )
        self.assertFalse(b.fits)
        self.assertLess(b.remaining, 0)

    def test_reserves_completion(self) -> None:
        b = plan("gpt-4o", user="hi", expected_completion=500)
        seg_names = [s.name for s in b.segments]
        self.assertIn("expected_completion", seg_names)
        completion_seg = next(s for s in b.segments if s.name == "expected_completion")
        self.assertEqual(completion_seg.tokens, 500)

    def test_safety_margin_applied(self) -> None:
        b_no_margin = plan("gpt-4o", user="hello world")
        b_with_margin = plan("gpt-4o", user="hello world", safety_margin=0.5)
        # 50% margin should push total higher
        self.assertGreater(b_with_margin.total_tokens, b_no_margin.total_tokens)

    def test_custom_model_limit(self) -> None:
        b = plan(
            "my-custom-model",
            user="hi",
            model_limits={"my-custom-model": 1000},
        )
        self.assertEqual(b.max_tokens, 1000)

    def test_unknown_model_defaults_to_8k(self) -> None:
        b = plan("never-heard-of-this-model", user="hi")
        self.assertEqual(b.max_tokens, 8192)

    def test_tools_tokens_counted(self) -> None:
        b = plan("gpt-4o", user="hi", tools_tokens=300)
        seg = next(s for s in b.segments if s.name == "tools")
        self.assertEqual(seg.tokens, 300)

    def test_to_dict_is_json_safe(self) -> None:
        import json
        b = plan("gpt-4o", system="x", user="y")
        # Must round-trip through JSON without TypeError
        json.dumps(b.to_dict())


class TestStrategy(unittest.TestCase):
    def test_strategy_field_present(self) -> None:
        b = plan("gpt-4o", user="hi")
        self.assertIn(b.strategy, {"tiktoken", "heuristic", "anthropic-heuristic"})

    def test_anthropic_strategy(self) -> None:
        b = plan("claude-3-5-sonnet", user="hi")
        self.assertEqual(b.strategy, "anthropic-heuristic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
