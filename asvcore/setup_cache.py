import json
import pickle

from .aux import set_cpu_affinity_from_params
from .discovery import get_benchmark_from_name


def _setup_cache(args):
    (benchmark_dir, benchmark_id, params_str) = args

    extra_params = json.loads(params_str)

    set_cpu_affinity_from_params(extra_params)

    benchmark = get_benchmark_from_name(benchmark_dir, benchmark_id)
    cache = benchmark.do_setup_cache()
    with open("cache.pickle", "wb") as fd:
        pickle.dump(cache, fd)
