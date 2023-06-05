import sys

from .aux import update_sys_path
from .discovery import disc_benchmarks


def _check(args):
    (benchmark_dir,) = args

    update_sys_path(benchmark_dir)

    ok = True
    for benchmark in disc_benchmarks(benchmark_dir):
        ok = ok and benchmark.check(benchmark_dir)

    sys.exit(0 if ok else 1)
