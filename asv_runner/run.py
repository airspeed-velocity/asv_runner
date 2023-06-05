import json
import math
import pickle

from .aux import set_cpu_affinity_from_params
from .discovery import get_benchmark_from_name


def _run(args):
    (benchmark_dir, benchmark_id, params_str, profile_path, result_file) = args

    extra_params = json.loads(params_str)

    set_cpu_affinity_from_params(extra_params)
    extra_params.pop("cpu_affinity", None)

    if profile_path == "None":
        profile_path = None

    benchmark = get_benchmark_from_name(
        benchmark_dir, benchmark_id, extra_params=extra_params
    )

    if benchmark.setup_cache_key is not None:
        with open("cache.pickle", "rb") as fd:
            cache = pickle.load(fd)
        if cache is not None:
            benchmark.insert_param(cache)

    skip = benchmark.do_setup()

    try:
        if skip:
            result = math.nan
        else:
            result = benchmark.do_run()
            if profile_path is not None:
                benchmark.do_profile(profile_path)
    finally:
        benchmark.do_teardown()

    # Write the output value
    with open(result_file, "w") as fp:
        json.dump(result, fp)
