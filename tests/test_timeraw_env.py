# Timeraw env design (asv#1471) + identity fingerprint.

import os
import sys
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from asv_runner.benchmarks.mark import benchmark  # noqa: E402
from asv_runner.benchmarks.timeraw import (TimerawBenchmark,  # noqa: E402
                                           _normalize_timeraw_env,
                                           _SeparateProcessTimer)


class TestTimerawEnvDesign(unittest.TestCase):
    def test_normalize_rejects_non_dict_and_none_values(self):
        self.assertIsNone(_normalize_timeraw_env(None))
        self.assertIsNone(_normalize_timeraw_env({}))
        with self.assertRaises(TypeError):
            _normalize_timeraw_env([("A", "1")])
        with self.assertRaises(TypeError):
            _normalize_timeraw_env({"A": None})

    def test_attribute_and_decorator_set_env(self):
        def timeraw_a():
            return "pass"

        timeraw_a.env = {"IS_PERF": "1"}
        b = TimerawBenchmark("m.timeraw_a", timeraw_a, [timeraw_a])
        b._load_vars()
        self.assertEqual(b._timeraw_env["IS_PERF"], "1")

        @benchmark(env={"IS_PERF": "2"})
        def timeraw_b():
            return "pass"

        b2 = TimerawBenchmark("m.timeraw_b", timeraw_b, [timeraw_b])
        b2._load_vars()
        self.assertEqual(b2._timeraw_env["IS_PERF"], "2")

    def test_child_environ_merge_and_override(self):
        timer = _SeparateProcessTimer(lambda: "pass", env={"PATH": "override-path"})
        child = timer._child_environ()
        self.assertEqual(child["PATH"], "override-path")
        if "HOME" in os.environ:
            self.assertEqual(child["HOME"], os.environ["HOME"])

    def test_timeit_sees_env_in_subprocess(self):
        def timeraw_probe():
            return """
            import os
            assert os.environ.get("ASV_TIMERAW_PROBE") == "yes"
            """

        timeraw_probe.env = {"ASV_TIMERAW_PROBE": "yes"}
        b = TimerawBenchmark("m.timeraw_probe", timeraw_probe, [timeraw_probe])
        b._load_vars()
        elapsed = b._get_timer().timeit(1)
        self.assertIsInstance(elapsed, float)

    def test_timer_does_not_renormalize(self):
        timer = _SeparateProcessTimer(lambda: "pass", env={"K": "v"})
        self.assertEqual(timer.env["K"], "v")

    def test_env_changes_default_version(self):
        def timeraw_x():
            return "pass"

        timeraw_x.env = {"A": "1"}
        b1 = TimerawBenchmark("m.timeraw_x", timeraw_x, [timeraw_x])

        def timeraw_y():
            return "pass"

        timeraw_y.env = {"A": "2"}
        b2 = TimerawBenchmark("m.timeraw_y", timeraw_y, [timeraw_y])
        self.assertNotEqual(b1.version, b2.version)

        def timeraw_z():
            return "pass"

        timeraw_z.env = {"A": "1"}
        timeraw_z.version = "fixed"
        b3 = TimerawBenchmark("m.timeraw_z", timeraw_z, [timeraw_z])
        self.assertEqual(b3.version, "fixed")

    def test_env_fingerprint_no_newline_or_equals_collision(self):
        from asv_runner.benchmarks.timeraw import _env_fingerprint

        a = _env_fingerprint({"A": "1\nB=2"})
        b = _env_fingerprint({"A": "1", "B": "2"})
        self.assertNotEqual(a, b)

        c = _env_fingerprint({"A": "B=1"})
        d = _env_fingerprint({"A=B": "1"})
        self.assertNotEqual(c, d)

        def timeraw_nl():
            return "pass"

        timeraw_nl.env = {"A": "1\nB=2"}
        b_nl = TimerawBenchmark("m.timeraw_nl", timeraw_nl, [timeraw_nl])

        def timeraw_two():
            return "pass"

        timeraw_two.env = {"A": "1", "B": "2"}
        b_two = TimerawBenchmark("m.timeraw_two", timeraw_two, [timeraw_two])
        self.assertNotEqual(b_nl.version, b_two.version)

        def timeraw_eq_val():
            return "pass"

        timeraw_eq_val.env = {"A": "B=1"}
        b_eq_val = TimerawBenchmark(
            "m.timeraw_eq_val", timeraw_eq_val, [timeraw_eq_val]
        )

        def timeraw_eq_key():
            return "pass"

        timeraw_eq_key.env = {"A=B": "1"}
        b_eq_key = TimerawBenchmark(
            "m.timeraw_eq_key", timeraw_eq_key, [timeraw_eq_key]
        )
        self.assertNotEqual(b_eq_val.version, b_eq_key.version)


if __name__ == "__main__":
    unittest.main()
