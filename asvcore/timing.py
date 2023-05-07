import json
import sys
import timeit
from time import process_time

from .benchmarks.time import TimeBenchmark


def _timing(argv):
    import argparse

    import asv.console
    import asv.statistics
    import asv.util

    parser = argparse.ArgumentParser(
        usage="python -masv.benchmark timing [options] STATEMENT"
    )
    parser.add_argument("--setup", action="store", default=(lambda: None))
    parser.add_argument("--number", action="store", type=int, default=0)
    parser.add_argument("--repeat", action="store", type=int, default=0)
    parser.add_argument(
        "--timer",
        action="store",
        choices=("process_time", "perf_counter"),
        default="perf_counter",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("statement")
    args = parser.parse_args(argv)

    timer_func = {
        "process_time": process_time,
        "perf_counter": timeit.default_timer,
    }[args.timer]

    class AttrSource:
        pass

    attrs = AttrSource()
    attrs.repeat = args.repeat
    attrs.number = args.number
    attrs.timer = timer_func

    bench = TimeBenchmark("tmp", args.statement, [attrs])
    bench.redo_setup = args.setup
    result = bench.run()

    value, stats = asv.statistics.compute_stats(result["samples"], result["number"])
    formatted = asv.util.human_time(value, asv.statistics.get_err(value, stats))

    if not args.json:
        asv.console.color_print(formatted, "red")
        asv.console.color_print("", "default")
        asv.console.color_print(
            "\n".join(f"{k}: {v}" for k, v in sorted(stats.items())), "default"
        )
        asv.console.color_print(f"samples: {result['samples']}", "default")
    else:
        json.dump(
            {"result": value, "samples": result["samples"], "stats": stats}, sys.stdout
        )
