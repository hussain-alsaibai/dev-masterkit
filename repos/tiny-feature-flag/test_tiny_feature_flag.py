"""Tests for tiny_feature_flag. Run with pytest or ``python test_tiny_feature_flag.py``."""
from __future__ import annotations

import unittest

from tiny_feature_flag import (
    Context,
    Flag,
    FlagNotFound,
    FlagStore,
    Rule,
)


class TestContext(unittest.TestCase):
    def test_get_user_dict_path(self):
        ctx = Context(user={"plan": "pro", "id": 42})
        self.assertEqual(ctx.get("user.plan"), "pro")
        self.assertEqual(ctx.get("user.id"), 42)
        self.assertIsNone(ctx.get("user.missing"))
        self.assertEqual(ctx.get("user.missing", "fallback"), "fallback")

    def test_get_attr_path(self):
        class User:
            def __init__(self):
                self.plan = "pro"
        ctx = Context(user=User())
        self.assertEqual(ctx.get("user.plan"), "pro")

    def test_get_extra_and_env(self):
        ctx = Context(env={"region": "us"}, extra={"x": 1})
        self.assertEqual(ctx.get("env.region"), "us")
        self.assertEqual(ctx.get("x"), 1)

    def test_empty_path_returns_user(self):
        ctx = Context(user={"a": 1})
        self.assertEqual(ctx.get(""), {"a": 1})

    def test_missing_user_does_not_raise(self):
        ctx = Context()
        self.assertIsNone(ctx.get("user.id"))


class TestRules(unittest.TestCase):
    def test_eq_match(self):
        rule = Rule.eq("user.plan", "pro")
        self.assertTrue(rule(Context(user={"plan": "pro"})))
        self.assertFalse(rule(Context(user={"plan": "free"})))
        self.assertIsNone(rule(Context()))  # missing path = defer

    def test_ne_match(self):
        rule = Rule.ne("user.plan", "free")
        self.assertTrue(rule(Context(user={"plan": "pro"})))
        self.assertFalse(rule(Context(user={"plan": "free"})))

    def test_in_match(self):
        rule = Rule.in_("user.email", ["a@x.com", "b@x.com"])
        self.assertTrue(rule(Context(user={"email": "a@x.com"})))
        self.assertFalse(rule(Context(user={"email": "c@x.com"})))
        self.assertIsNone(rule(Context()))

    def test_contains(self):
        rule = Rule.contains("user.roles", "admin")
        self.assertTrue(rule(Context(user={"roles": ["admin", "user"]})))
        self.assertFalse(rule(Context(user={"roles": ["user"]})))
        self.assertFalse(rule(Context(user={"roles": "not_iterable_here_but_string"})))
        # missing path = defer
        self.assertIsNone(rule(Context()))

    def test_predicate(self):
        rule = Rule.predicate(lambda c: True)
        self.assertTrue(rule(Context()))
        rule = Rule.predicate(lambda c: False)
        self.assertIsNone(rule(Context()))  # False -> None (defer)

    def test_percent_distribution(self):
        rule = Rule.percent("user.id", 50, salt="dark_mode")
        # Run many users; should be roughly 50/50
        yes = sum(1 for i in range(2000) if rule(Context(user={"id": f"u{i}"})))
        self.assertGreater(yes, 850)
        self.assertLess(yes, 1150)

    def test_percent_stable_per_user(self):
        rule = Rule.percent("user.id", 50, salt="x")
        v1 = rule(Context(user={"id": "u123"}))
        v2 = rule(Context(user={"id": "u123"}))
        self.assertEqual(v1, v2)

    def test_percent_zero_always_false(self):
        rule = Rule.percent("user.id", 0)
        for i in range(100):
            self.assertFalse(rule(Context(user={"id": f"u{i}"})))

    def test_percent_hundred_always_true(self):
        rule = Rule.percent("user.id", 100)
        for i in range(100):
            self.assertTrue(rule(Context(user={"id": f"u{i}"})))

    def test_percent_invalid_raises(self):
        with self.assertRaises(ValueError):
            Rule.percent("user.id", -1)
        with self.assertRaises(ValueError):
            Rule.percent("user.id", 101)


class TestFlag(unittest.TestCase):
    def test_default_when_no_rules(self):
        flag = Flag(name="x", default=True)
        self.assertTrue(flag.evaluate(Context()))
        flag = Flag(name="x", default=False)
        self.assertFalse(flag.evaluate(Context()))

    def test_first_matching_rule_wins(self):
        flag = Flag(
            name="x",
            default=False,
            rules=[Rule.eq("user.plan", "pro"), Rule.eq("user.plan", "free")],
        )
        # pro -> True; free -> False; missing -> default (False)
        self.assertTrue(flag.evaluate(Context(user={"plan": "pro"})))
        self.assertFalse(flag.evaluate(Context(user={"plan": "free"})))
        self.assertFalse(flag.evaluate(Context(user={"plan": "enterprise"})))

    def test_override_wins_over_rules(self):
        flag = Flag(name="x", default=False, rules=[Rule.eq("user.plan", "pro")])
        flag.add_override("user.id", "u1", True)
        # u1 is on free plan but override forces on
        self.assertTrue(flag.evaluate(Context(user={"id": "u1", "plan": "free"})))
        # u2 is on pro plan and rule fires
        self.assertTrue(flag.evaluate(Context(user={"id": "u2", "plan": "pro"})))
        # u3 has no rule and no override, defaults off
        self.assertFalse(flag.evaluate(Context(user={"id": "u3", "plan": "free"})))

    def test_override_can_force_off(self):
        flag = Flag(name="x", default=True)
        flag.add_override("user.id", "u1", False)
        self.assertFalse(flag.evaluate(Context(user={"id": "u1"})))
        self.assertTrue(flag.evaluate(Context(user={"id": "u2"})))


class TestFlagStore(unittest.TestCase):
    def test_construct_from_mapping(self):
        store = FlagStore({
            "a": Flag(name="a", default=True),
            "b": Flag(name="b", default=False),
        })
        self.assertEqual(store.names(), ["a", "b"])
        self.assertTrue(store.enabled("a"))
        self.assertFalse(store.enabled("b"))

    def test_name_mismatch_raises(self):
        with self.assertRaises(ValueError):
            FlagStore({"a": Flag(name="b", default=True)})

    def test_register_unregister(self):
        store = FlagStore()
        store.register(Flag(name="x", default=True))
        self.assertIn("x", store.names())
        store.unregister("x")
        self.assertNotIn("x", store.names())
        # unknown is no-op
        store.unregister("nope")

    def test_double_register_raises(self):
        store = FlagStore()
        store.register(Flag(name="x", default=True))
        with self.assertRaises(ValueError):
            store.register(Flag(name="x", default=False))

    def test_unknown_raises_flag_not_found(self):
        store = FlagStore()
        with self.assertRaises(FlagNotFound):
            store.enabled("nope")

    def test_evaluate_all(self):
        store = FlagStore({
            "a": Flag(name="a", default=True),
            "b": Flag(name="b", default=False),
        })
        result = store.evaluate_all(Context())
        self.assertEqual(result, {"a": True, "b": False})

    def test_thread_safety(self):
        import threading
        store = FlagStore({"a": Flag(name="a", default=True)})
        errors = []

        def reader():
            try:
                for _ in range(1000):
                    store.enabled("a")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])


class TestIntegration(unittest.TestCase):
    def test_dark_mode_rollout(self):
        # Realistic scenario: dark mode for pro users, with a 20% rollout
        # to free users on user.id hash.
        dark = Flag(
            name="dark_mode",
            default=False,
            rules=[
                Rule.matches(lambda v: v == "pro", "user.plan"),
                Rule.percent("user.id", 20, salt="dark_mode"),
            ],
        )
        store = FlagStore({"dark_mode": dark})

        # Pro users always see it
        for i in range(50):
            self.assertTrue(store.enabled("dark_mode", Context(user={"id": f"u{i}", "plan": "pro"})))

        # Free users: ~20%
        yes = sum(
            1 for i in range(2000)
            if store.enabled("dark_mode", Context(user={"id": f"u{i}", "plan": "free"}))
        )
        self.assertGreater(yes, 300)
        self.assertLess(yes, 500)

    def test_canary_with_override(self):
        # Beta users see v2; everyone else on v1.
        v2 = Flag(
            name="v2_endpoint",
            default=False,
            rules=[Rule.contains("user.groups", "beta")],
        )
        v2.add_override("user.id", "ops", True)  # ops always on v2
        store = FlagStore({"v2_endpoint": v2})

        self.assertTrue(store.enabled("v2_endpoint", Context(user={"id": "ops", "groups": []})))
        self.assertTrue(store.enabled("v2_endpoint", Context(user={"id": "u1", "groups": ["beta"]})))
        self.assertFalse(store.enabled("v2_endpoint", Context(user={"id": "u1", "groups": []})))


if __name__ == "__main__":
    unittest.main()
