import re
import sys
import timeit

from ._base import Benchmark, _get_first_attr

wall_timer = timeit.default_timer


class TimeBenchmark(Benchmark):
    """
    Represents a single benchmark for timing.
    """

    name_regex = re.compile("^(Time[A-Z_].+)|(time_.+)$")

    def __init__(self, name, func, attr_sources):
        Benchmark.__init__(self, name, func, attr_sources)
        self.type = "time"
        self.unit = "seconds"
        self._attr_sources = attr_sources
        old = int(
            _get_first_attr(self._attr_sources, "processes", 2)
        )  # backward compat.
        self.rounds = int(_get_first_attr(self._attr_sources, "rounds", old))
        self._load_vars()

    def _load_vars(self):
        self.repeat = _get_first_attr(self._attr_sources, "repeat", 0)
        self.min_run_count = _get_first_attr(self._attr_sources, "min_run_count", 2)
        self.number = int(_get_first_attr(self._attr_sources, "number", 0))
        self.sample_time = _get_first_attr(self._attr_sources, "sample_time", 0.01)
        self.warmup_time = _get_first_attr(self._attr_sources, "warmup_time", -1)
        self.timer = _get_first_attr(self._attr_sources, "timer", wall_timer)

    def do_setup(self):
        result = Benchmark.do_setup(self)
        # For parameterized tests, setup() is allowed to change these
        self._load_vars()
        return result

    def _get_timer(self, *param):
        if param:

            def func():
                self.func(*param)

        else:
            func = self.func

        timer = timeit.Timer(stmt=func, setup=self.redo_setup, timer=self.timer)

        return timer

    def run(self, *param):
        warmup_time = self.warmup_time
        if warmup_time < 0:
            if "__pypy__" in sys.modules:
                warmup_time = 1.0
            elif "__graalpython__" in sys.modules:
                warmup_time = 5.0
            else:
                # Transient effects exist also on CPython, e.g. from
                # OS scheduling
                warmup_time = 0.1

        timer = self._get_timer(*param)

        try:
            min_repeat, max_repeat, max_time = self.repeat
        except (ValueError, TypeError):
            if self.repeat == 0:
                min_repeat = 1
                max_repeat = 10
                max_time = 20.0
                if self.rounds > 1:
                    max_repeat //= 2
                    max_time /= 2.0
            else:
                min_repeat = self.repeat
                max_repeat = self.repeat
                max_time = self.timeout

        min_repeat = int(min_repeat)
        max_repeat = int(max_repeat)
        max_time = float(max_time)

        samples, number = self.benchmark_timing(
            timer,
            min_repeat,
            max_repeat,
            max_time=max_time,
            warmup_time=warmup_time,
            number=self.number,
            min_run_count=self.min_run_count,
        )

        samples = [s / number for s in samples]
        return {"samples": samples, "number": number}

    def benchmark_timing(
        self,
        timer,
        min_repeat,
        max_repeat,
        max_time,
        warmup_time,
        number,
        min_run_count,
    ):
        sample_time = self.sample_time
        start_time = wall_timer()
        run_count = 0

        samples = []

        def too_slow(num_samples):
            # stop taking samples if limits exceeded
            if run_count < min_run_count:
                return False
            if num_samples < min_repeat:
                return False
            return wall_timer() > start_time + warmup_time + max_time

        if number == 0:
            # Select number & warmup.
            #
            # This needs to be done at the same time, because the
            # benchmark timings at the beginning can be larger, and
            # lead to too small number being selected.
            number = 1
            while True:
                self._redo_setup_next = False
                start = wall_timer()
                timing = timer.timeit(number)
                wall_time = wall_timer() - start
                actual_timing = max(wall_time, timing)
                run_count += number

                if actual_timing >= sample_time:
                    if wall_timer() > start_time + warmup_time:
                        break
                else:
                    try:
                        p = min(10.0, max(1.1, sample_time / actual_timing))
                    except ZeroDivisionError:
                        p = 10.0
                    number = max(number + 1, int(p * number))

            if too_slow(1):
                return [timing], number
        elif warmup_time > 0:
            # Warmup
            while True:
                self._redo_setup_next = False
                timing = timer.timeit(number)
                run_count += number
                if wall_timer() >= start_time + warmup_time:
                    break

            if too_slow(1):
                return [timing], number

        # Collect samples
        while len(samples) < max_repeat:
            timing = timer.timeit(number)
            run_count += number
            samples.append(timing)

            if too_slow(len(samples)):
                break

        return samples, number


export_as_benchmark = [TimeBenchmark]
