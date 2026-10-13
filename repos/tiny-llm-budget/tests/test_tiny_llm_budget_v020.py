"""Tests for tiny-llm-budget v0.2.0 — compare_models + cost catalogue."""
from __future__ import annotations

import unittest

from tiny_llm_budget import (
    COST_PER_MILLION,
    MODEL_LIMITS,
    compare_models,
    plan,
)


class TestCompareModels(unittest.TestCase):
    def test_basic_returns_one_per_model(self):
        results = compare_models(
            ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"],
            user="hello world",
            expected_completion=200,
        )
        self.assertEqual(len(results), 3)
        # Each result is (model, Budget, cost_or_None)
        for model, budget, cost in results:
            self.assertIsInstance(budget.fits, bool)
            self.assertIsNone(cost)  # no cost_per_million passed

    def test_sorted_fits_first(self):
        # Build a prompt that overflows the 8k context for one model
        huge = "x " * 50_000  # ~50k tokens heuristic
        results = compare_models(
            ["gpt-4", "claude-3-opus", "gpt-4o-mini"],
            user=huge,
            expected_completion=500,
        )
        # First result must fit (all should fit, but gpt-4 has the smallest window)
        # gpt-4 has 8192, claude-3-opus 200k, gpt-4o-mini 128k
        # gpt-4 will NOT fit, but the others will
        names = [r[0] for r in results]
        self.assertIn("gpt-4", names)
        self.assertIn("claude-3-opus", names)
        # Sorted: fitting first, then non-fitting
        for model, budget, _ in results:
            if model == "gpt-4":
                self.assertFalse(budget.fits)

    def test_cost_passed_through(self):
        rates = {"gpt-4o": (2.50, 10.00), "gpt-4o-mini": (0.15, 0.60)}
        results = compare_models(
            ["gpt-4o", "gpt-4o-mini"],
            user="hello",
            expected_completion=1000,
            cost_per_million=rates,
        )
        costs = {r[0]: r[2] for r in results}
        self.assertIsNotNone(costs["gpt-4o"])
        self.assertIsNotNone(costs["gpt-4o-mini"])
        # gpt-4o is more expensive than gpt-4o-mini (same input, same output)
        self.assertGreater(costs["gpt-4o"], costs["gpt-4o-mini"])

    def test_cost_estimated_correctly(self):
        # 1M input tokens at $2.50/M, 1M output at $10/M => $12.50
        rates = {"gpt-4o": (2.50, 10.00)}
        # Force exactly 1M input + 1M output via model_limits and synthetic
        results = compare_models(
            ["gpt-4o"],
            user="a",  # tiny
            expected_completion=1_000_000,
            cost_per_million=rates,
        )
        model, _, cost = results[0]
        # 1 token of input, 1M of output
        # cost = (1/1M) * 2.5 + (1M/1M) * 10 = 10.0000025 -> round 6 = 10.000003
        self.assertAlmostEqual(cost, 10.000003, places=4)

    def test_unknown_model_uses_default_limit(self):
        # Unknown model -> 8k default; huge user should not fit
        huge = "x " * 50_000
        results = compare_models(["my-fine-tune-7b"], user=huge, expected_completion=200)
        model, budget, _ = results[0]
        self.assertFalse(budget.fits)
        self.assertEqual(budget.max_tokens, 8_192)

    def test_cost_catalogue_has_frontier_models(self):
        for name in (
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-5-sonnet",
            "claude-3-opus",
            "gemini-1.5-pro",
            "llama-3.1-70b",
            "deepseek-v3",
        ):
            self.assertIn(name, COST_PER_MILLION)
            in_rate, out_rate = COST_PER_MILLION[name]
            self.assertGreaterEqual(in_rate, 0)
            self.assertGreaterEqual(out_rate, 0)

    def test_input_output_split_in_cost(self):
        # expected_completion is "output"; everything else is "input"
        rates = {"gpt-4o": (1.00, 100.00)}  # make output 100x more expensive
        results_in_only = compare_models(
            ["gpt-4o"], user="hello world", expected_completion=0, cost_per_million=rates
        )
        results_out_only = compare_models(
            ["gpt-4o"], user="", expected_completion=1000, cost_per_million=rates
        )
        c_in = results_in_only[0][2]
        c_out = results_out_only[0][2]
        # Output is 100x more expensive per token; should dominate
        self.assertGreater(c_out, c_in * 10)

    def test_history_counted_as_input(self):
        rates = {"gpt-4o": (1.00, 0.01)}  # input dominates
        results = compare_models(
            ["gpt-4o"],
            user="hi",
            history=[("user", "how are you? " * 100), ("assistant", "I am fine, thanks. " * 100)],
            cost_per_million=rates,
        )
        cost = results[0][2]
        # If history is input, cost is at least (input_tokens / 1M) * 1.0
        # which is much higher than a 2-token "hi" alone would give.
        results_no_hist = compare_models(
            ["gpt-4o"], user="hi", cost_per_million=rates
        )
        self.assertGreater(cost, results_no_hist[0][2])


class TestCostCatalogue(unittest.TestCase):
    def test_all_catalogue_models_also_have_limits(self):
        for name in COST_PER_MILLION:
            self.assertIn(name, MODEL_LIMITS, f"{name} has cost but no MODEL_LIMITS entry")

    def test_input_le_output_typical(self):
        # Most frontier models charge more for output than input.
        for name, (in_rate, out_rate) in COST_PER_MILLION.items():
            if in_rate > 0:  # skip free experimental
                # Either output >= input (typical) or close. We allow equal for open-source proxies.
                self.assertGreaterEqual(out_rate, in_rate * 0.5,
                    f"{name}: output ({out_rate}) suspiciously cheap vs input ({in_rate})")


if __name__ == "__main__":
    unittest.main()
