from functools import wraps


def skip_benchmark(func):
    """
    Decorator to mark a function as skipped for benchmarking.

    #### Parameters
    **func** (function)
    : The function to be marked as skipped.

    #### Returns
    **wrapper** (function)
    : A wrapped function that is marked to be skipped for benchmarking.

    #### Notes
    The `skip_benchmark` decorator can be used to mark a specific function as
    skipped for benchmarking. When the decorated function is encountered during
    benchmarking, it will be skipped and not included in the benchmarking
    process.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(wrapper, "skip_benchmark", True)
    return wrapper
