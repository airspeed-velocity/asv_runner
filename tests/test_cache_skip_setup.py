# Regression tests for asv_runner#49 and airspeed-velocity/asv#1592.
# Drive shipped Benchmark / mark APIs only (no re-implementation).


import os
import sys
import unittest

# Allow running without install: repo root on path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from asv_runner.benchmarks._base import Benchmark  # noqa: E402
from asv_runner.benchmarks.mark import benchmark, skip_for_params  # noqa: E402
from asv_runner.benchmarks.track import TrackBenchmark  # noqa: E402


def _make_track_benchmark(func, name="mod.track_x"):
    """Build a real TrackBenchmark from a plain function (shipped ctor)."""
    # attr_sources: function first so decorators / attrs on func win.
    return TrackBenchmark(name, func, [func])


class TestCacheSkipAndSetup(unittest.TestCase):
    def test_skip_params_ignores_cache_object(self):
        # Declared skip is (2,); cache must not be part of the skip key.
        @skip_for_params([(2,)])
        def track_fn(cache, n):
            return n

        track_fn.params = [1, 2]
        track_fn.param_names = ["n"]

        b = _make_track_benchmark(track_fn, "mod.track_fn")
        self.assertEqual(b._skip_tuples, [(2,)])

        b.set_param_idx(1)  # n == 2
        cache_obj = {"payload": 99}
        b.set_cache(cache_obj)

        # Skip key is declared params only (asv_runner#49).
        self.assertTrue(b.do_setup())
        self.assertIsNone(b.do_run())
        self.assertEqual(b._build_params(), (cache_obj, 2))

        b.set_param_idx(0)  # n == 1 — not skipped
        b.set_cache(cache_obj)
        self.assertFalse(b.do_setup())
        self.assertEqual(b.do_run(), 1)

    def test_falsy_cache_still_prepended(self):
        def track_fn(cache, n):
            return (cache, n)

        track_fn.params = [3]
        b = _make_track_benchmark(track_fn, "mod.track_falsy")
        b.set_param_idx(0)
        for falsy in (0, [], {}, ""):
            b.set_cache(falsy)
            self.assertEqual(b._build_params(), (falsy, 3))
            self.assertEqual(b.do_run(), (falsy, 3))

    def test_none_cache_does_not_prepend(self):
        def track_fn(n):
            return n

        track_fn.params = [4]
        b = _make_track_benchmark(track_fn, "mod.track_none_cache")
        b.set_param_idx(0)
        b.set_cache(None)
        self.assertEqual(b._build_params(), (4,))
        self.assertEqual(b.do_run(), 4)

    def test_parameter_free_setup_runs_before_setup_cache(self):
        order = []

        def module_setup(*args, **kwargs):
            order.append("module_setup")

        def class_setup(n):
            order.append("class_setup")
            raise AssertionError("class setup must not run in do_setup_cache")

        def setup_cache():
            order.append("setup_cache")
            return {"ok": True}

        def track_fn(cache, n):
            return n

        track_fn.params = [1]
        track_fn.setup = class_setup
        track_fn.setup_cache = setup_cache

        b = _make_track_benchmark(track_fn, "mod.track_seed")
        # Inject module-level setup at front of MRO-style list (as discovery does).
        b._setups = [module_setup, class_setup]
        b._setup_cache = setup_cache

        out = b.do_setup_cache()
        self.assertEqual(out, {"ok": True})
        self.assertEqual(order, ["module_setup", "setup_cache"])
        self.assertTrue(Benchmark._is_parameter_free_setup(module_setup))
        self.assertFalse(Benchmark._is_parameter_free_setup(class_setup))

    def test_benchmark_decorator_attrs_and_unknown(self):
        @benchmark(pretty_name="Pretty", timeout=12.5, max_time=30.0)
        def track_fn():
            return 0

        self.assertEqual(track_fn.pretty_name, "Pretty")
        self.assertEqual(track_fn.timeout, 12.5)
        self.assertEqual(track_fn.max_time, 30.0)

        with self.assertRaises(TypeError) as ctx:

            @benchmark(not_a_real_attr=1)
            def bad():
                pass

        self.assertIn("Unknown benchmark attribute", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
