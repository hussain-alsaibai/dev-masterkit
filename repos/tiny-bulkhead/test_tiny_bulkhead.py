"""Tests for tiny_bulkhead. Run with ``python -m pytest`` or ``python test_tiny_bulkhead.py``."""
from __future__ import annotations

import asyncio
import threading
import time
import unittest

from tiny_bulkhead import (
    Bulkhead,
    BulkheadFull,
    BulkheadPool,
    BulkheadStats,
)


class TestBulkheadBasics(unittest.TestCase):
    def test_construction_validates(self):
        with self.assertRaises(ValueError):
            Bulkhead("x", max_concurrent=0)
        with self.assertRaises(ValueError):
            Bulkhead("x", max_concurrent=1, timeout=-1)
        with self.assertRaises(ValueError):
            Bulkhead("x", max_concurrent=1, call_timeout=0)

    def test_acquire_release_roundtrip(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        bh.acquire()
        self.assertEqual(bh.in_flight, 1)
        bh.release()
        self.assertEqual(bh.in_flight, 0)

    def test_context_manager(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        with bh:
            self.assertEqual(bh.in_flight, 1)
        self.assertEqual(bh.in_flight, 0)

    def test_context_manager_releases_on_exception(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        try:
            with bh:
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        self.assertEqual(bh.in_flight, 0)
        self.assertEqual(bh.stats().failed, 1)
        self.assertEqual(bh.stats().completed, 0)

    def test_full_raises_immediately_with_timeout_zero(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        bh.acquire()
        with self.assertRaises(BulkheadFull):
            bh.acquire()
        self.assertEqual(bh.stats().rejected, 1)

    def test_wait_then_acquire(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0.5)
        bh.acquire()

        def releaser():
            time.sleep(0.05)
            bh.release()

        threading.Thread(target=releaser, daemon=True).start()
        bh.acquire()  # should succeed within 0.5s
        bh.release()
        self.assertGreaterEqual(bh.stats().acquired, 2)

    def test_wait_timeout(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0.05)
        bh.acquire()
        start = time.monotonic()
        with self.assertRaises(BulkheadFull):
            bh.acquire()
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, 0.04)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(bh.stats().rejected, 1)


class TestBulkheadRun(unittest.TestCase):
    def test_run_returns_value(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        result = bh.run(lambda x: x * 2, 21)
        self.assertEqual(result, 42)
        self.assertEqual(bh.stats().completed, 1)

    def test_run_propagates_exception(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        with self.assertRaises(ValueError):
            bh.run(lambda: (_ for _ in ()).throw(ValueError("boom")))
        self.assertEqual(bh.stats().failed, 1)

    def test_run_async_returns_value(self):
        async def go():
            bh = Bulkhead("t", max_concurrent=1, timeout=0)

            async def add_one(x):
                return x + 1

            return await bh.run_async(add_one, 41)

        result = asyncio.run(go())
        self.assertEqual(result, 42)

    def test_run_async_propagates_exception(self):
        async def go():
            bh = Bulkhead("t", max_concurrent=1, timeout=0)
            await bh.run_async(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

        with self.assertRaises(RuntimeError):
            asyncio.run(go())

    def test_async_with(self):
        async def go():
            bh = Bulkhead("t", max_concurrent=1, timeout=0)
            async with bh() as b:
                self.assertIs(b, bh)
                self.assertEqual(bh.in_flight, 1)
            self.assertEqual(bh.in_flight, 0)

        asyncio.run(go())


class TestBulkheadStats(unittest.TestCase):
    def test_stats_initial(self):
        bh = Bulkhead("openai", max_concurrent=4)
        s = bh.stats()
        self.assertIsInstance(s, BulkheadStats)
        self.assertEqual(s.name, "openai")
        self.assertEqual(s.max_concurrent, 4)
        self.assertEqual(s.in_flight, 0)
        self.assertEqual(s.acquired, 0)

    def test_stats_to_dict_is_json_safe(self):
        import json
        bh = Bulkhead("openai", max_concurrent=4)
        bh.acquire()
        d = bh.stats().to_dict()
        # must serialise
        json.dumps(d)
        bh.release()

    def test_reset_stats(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        bh.acquire()
        bh.release()
        self.assertEqual(bh.stats().acquired, 1)
        bh.reset_stats()
        self.assertEqual(bh.stats().acquired, 0)

    def test_release_without_acquire_is_safe(self):
        bh = Bulkhead("t", max_concurrent=1, timeout=0)
        # should NOT raise
        bh.release()
        bh.release(success=False)


class TestBulkheadPool(unittest.TestCase):
    def test_construction_from_dict(self):
        pool = BulkheadPool({"openai": 4, "anthropic": 2})
        self.assertEqual(pool.names(), ["anthropic", "openai"])
        self.assertEqual(pool.bulkhead("openai").max_concurrent, 4)

    def test_construction_from_pairs(self):
        pool = BulkheadPool([("a", 1), ("b", 2)])
        self.assertEqual(pool.bulkhead("a").max_concurrent, 1)

    def test_lookup_unknown_raises(self):
        pool = BulkheadPool({"a": 1})
        with self.assertRaises(KeyError):
            pool.bulkhead("nope")

    def test_double_register_raises(self):
        pool = BulkheadPool()
        pool.register("a", 1)
        with self.assertRaises(ValueError):
            pool.register("a", 2)

    def test_stats_returns_all(self):
        pool = BulkheadPool({"a": 1, "b": 2})
        pool.bulkhead("a").acquire()
        stats = pool.stats()
        self.assertIn("a", stats)
        self.assertIn("b", stats)
        self.assertEqual(stats["a"].in_flight, 1)
        self.assertEqual(stats["b"].in_flight, 0)
        pool.bulkhead("a").release()


class TestBulkheadConcurrency(unittest.TestCase):
    def test_concurrent_acquires_respect_cap(self):
        # N threads race for a cap of K.  In_flight must never exceed K
        # at any point, and the rejected count must equal N - K (since
        # we use timeout=0 and only K threads can hold a slot at a time).
        cap = 3
        n_threads = cap + 4
        bh = Bulkhead("t", max_concurrent=cap, timeout=0.01)
        in_flight_peak = 0
        peak_lock = threading.Lock()
        start = threading.Event()

        def worker():
            start.wait()
            try:
                with bh:
                    with peak_lock:
                        nonlocal in_flight_peak
                        in_flight_peak = max(in_flight_peak, bh.in_flight)
                    time.sleep(0.02)
            except BulkheadFull:
                pass

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        start.set()
        for t in threads:
            t.join(timeout=3)
            self.assertFalse(t.is_alive(), "thread hung")

        self.assertLessEqual(in_flight_peak, cap)
        # Every thread should be accounted for: completed + failed + rejected
        s = bh.stats()
        self.assertEqual(s.completed + s.rejected, n_threads)

    def test_bulkhead_pool_isolates_providers(self):
        pool = BulkheadPool({"slow": 1, "fast": 4}, default_timeout=0.5)
        # Saturate slow
        pool.bulkhead("slow").acquire()
        # Slow is full - next acquire raises
        with self.assertRaises(BulkheadFull):
            pool.bulkhead("slow").acquire()
        # But fast still has 4 slots
        for _ in range(4):
            pool.bulkhead("fast").acquire()
        self.assertEqual(pool.bulkhead("slow").in_flight, 1)
        self.assertEqual(pool.bulkhead("fast").in_flight, 4)


if __name__ == "__main__":
    unittest.main()
