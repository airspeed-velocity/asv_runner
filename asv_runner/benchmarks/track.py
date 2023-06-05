import re

from ._base import Benchmark, _get_first_attr


class TrackBenchmark(Benchmark):
    """
    Represents a single benchmark for tracking an arbitrary value.
    """

    name_regex = re.compile("^(Track[A-Z_].+)|(track_.+)$")

    def __init__(self, name, func, attr_sources):
        Benchmark.__init__(self, name, func, attr_sources)
        self.type = _get_first_attr(attr_sources, "type", "track")
        self.unit = _get_first_attr(attr_sources, "unit", "unit")

    def run(self, *param):
        return self.func(*param)


export_as_benchmark = [TrackBenchmark]
