import copy
import re

from ._base import Benchmark
from ._exceptions import NotRequired

try:
    from pympler.asizeof import asizeof
except ImportError:
    raise NotRequired("MemBenchmarks not requested or pympler not found")


class MemBenchmark(Benchmark):
    """
    Represents a single benchmark for tracking the memory consumption
    of an object.
    """

    name_regex = re.compile("^(Mem[A-Z_].+)|(mem_.+)$")

    def __init__(self, name, func, attr_sources):
        Benchmark.__init__(self, name, func, attr_sources)
        self.type = "memory"
        self.unit = "bytes"

    def run(self, *param):
        obj = self.func(*param)

        sizeof2 = asizeof([obj, obj])
        sizeofcopy = asizeof([obj, copy.copy(obj)])

        return sizeofcopy - sizeof2


export_as_benchmark = [MemBenchmark]
