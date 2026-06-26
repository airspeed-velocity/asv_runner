# asv_runner#43 hashing + asv_runner#33 timing scale regression.
from __future__ import print_function

import os
import sys
import time
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from asv_runner.benchmarks._base import code_fingerprint  # noqa: E402
from asv_runner.benchmarks.time import TimeBenchmark  # noqa: E402


class TestCodeFingerprint(unittest.TestCase):
    def test_whitespace_and_comment_stable(self):
        a = "def f():\n    return 1 + 2\n"
        b = "def f():\n    return 1+2  # trailing comment\n"
        self.assertEqual(code_fingerprint(a), code_fingerprint(b))

    def test_semantic_change_differs(self):
        a = "def f():\n    return 1\n"
        b = "def f():\n    return 2\n"
        self.assertNotEqual(code_fingerprint(a), code_fingerprint(b))


class TestTimingScale(unittest.TestCase):
    """asv_runner#33: samples are per-call seconds, not systematically ~half."""

    def test_sleep_sample_near_wall_duration(self):
        delay = 0.05

        def time_sleep():
            time.sleep(delay)

        time_sleep.number = 1
        time_sleep.repeat = 3
        time_sleep.warmup_time = 0
        time_sleep.sample_time = 0.01
        time_sleep.min_run_count = 1
        time_sleep.rounds = 1
        time_sleep.processes = 1

        b = TimeBenchmark("m.time_sleep", time_sleep, [time_sleep])
        b._load_vars()
        result = b.run()
        samples = result["samples"]
        self.assertEqual(result["number"], 1)
        # Each sample is total timeit time / number => ~delay seconds.
        median = sorted(samples)[len(samples) // 2]
        # Allow OS scheduling noise; fail if ~50% systematic (would be ~0.025).
        self.assertGreater(median, delay * 0.7, msg="samples=%r" % (samples,))
        self.assertLess(median, delay * 2.5, msg="samples=%r" % (samples,))


if __name__ == "__main__":
    unittest.main()
