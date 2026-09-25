"""
Tests for collection of arbitrary user-defined attributes onto a benchmark
instance (asv_runner#55).
"""

import os
import sys
import unittest

# Allow running without install: repo root on path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from asv_runner.benchmarks.track import TrackBenchmark


class DummyBenchmarks:
    """Container standing in for a user's benchmark module/class."""

    def track_mem_bw(self):
        return 123.4

    track_mem_bw.unit = "MB/s"
    track_mem_bw.some_boolean = True
    track_mem_bw._hidden = "should not be copied"
    track_mem_bw.some_callback = lambda: None


class TestDynamicAttrs(unittest.TestCase):
    def setUp(self):
        self.instance = DummyBenchmarks()
        # func first, so _get_first_attr("unit", ...) finds it, mirroring
        # how real asv discovery builds attr_sources.
        self.attr_sources = [self.instance.track_mem_bw, self.instance]
        self.benchmark = TrackBenchmark(
            "track_mem_bw", self.instance.track_mem_bw, self.attr_sources
        )

    def test_track_benchmark_constructs(self):
        # Regression test: constructing a benchmark must not raise, even though
        # _collect_dynamic_attrs is invoked from __init__ as ``self._collect_...``.
        assert self.benchmark.name == "track_mem_bw"

    def test_dynamic_user_attr_lands_on_instance(self):
        # user-defined, non-callable attribute set on the function is copied over
        assert self.benchmark.some_boolean is True

    def test_existing_attrs_are_not_overwritten(self):
        # `unit` is resolved by TrackBenchmark via _get_first_attr(attr_sources, "unit", ...)
        # *after* Benchmark.__init__ (and thus _collect_dynamic_attrs) has already run,
        # so it must end up as "MB/s", not silently reset to the "unit" default.
        assert self.benchmark.unit == "MB/s"

    def test_callable_and_private_attrs_are_ignored(self):
        assert not hasattr(self.benchmark, "_hidden")
        assert not hasattr(self.benchmark, "some_callback")


if __name__ == "__main__":
    unittest.main()
