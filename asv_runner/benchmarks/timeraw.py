import re
import subprocess
import sys
import textwrap

from ._base import _get_first_attr
from .time import TimeBenchmark


class _SeparateProcessTimer:
    subprocess_tmpl = textwrap.dedent(
        '''
        from __future__ import print_function
        from timeit import timeit, default_timer as timer
        print(repr(timeit(stmt="""{stmt}""", setup="""{setup}""",
                    number={number}, timer=timer)))
    '''
    ).strip()

    def __init__(self, func):
        self.func = func

    def timeit(self, number):
        stmt = self.func()
        if isinstance(stmt, tuple):
            stmt, setup = stmt
        else:
            setup = ""
        stmt = textwrap.dedent(stmt)
        setup = textwrap.dedent(setup)
        stmt = stmt.replace(r'"""', r"\"\"\"")
        setup = setup.replace(r'"""', r"\"\"\"")

        code = self.subprocess_tmpl.format(stmt=stmt, setup=setup, number=number)

        res = subprocess.check_output([sys.executable, "-c", code])
        return float(res.strip())


class TimerawBenchmark(TimeBenchmark):
    """
    Represents a benchmark for tracking timing benchmarks run once in
    a separate process.
    """

    name_regex = re.compile("^(Timeraw[A-Z_].+)|(timeraw_.+)$")

    def _load_vars(self):
        TimeBenchmark._load_vars(self)
        self.number = int(_get_first_attr(self._attr_sources, "number", 1))
        del self.timer

    def _get_timer(self, *param):
        if param:

            def func():
                self.func(*param)

        else:
            func = self.func
        return _SeparateProcessTimer(func)

    def do_profile(self, filename=None):
        raise ValueError("Raw timing benchmarks cannot be profiled")


export_as_benchmark = [TimerawBenchmark]
