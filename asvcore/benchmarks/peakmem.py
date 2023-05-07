import re

from ._base import Benchmark
from ._maxrss import get_maxrss


class PeakMemBenchmark(Benchmark):
    """
    Represents a single benchmark for tracking the peak memory consumption
    of the whole program.
    """

    name_regex = re.compile("^(PeakMem[A-Z_].+)|(peakmem_.+)$")

    def __init__(self, name, func, attr_sources):
        Benchmark.__init__(self, name, func, attr_sources)
        self.type = "peakmemory"
        self.unit = "bytes"

    def run(self, *param):
        self.func(*param)
        return get_maxrss()


export_as_benchmark = [PeakMemBenchmark]
