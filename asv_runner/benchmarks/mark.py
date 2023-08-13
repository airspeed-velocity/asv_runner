import functools


def skip_for_params(skip_params_list):
    """
    Decorator to set skip parameters for a benchmark function.

    #### Parameters
    **skip_params_dict** (`dict`):
    A dictionary specifying the skip parameters for the benchmark function.
    The keys represent the parameter names, and the values can be a single value
    or a list of values.

    #### Returns
    **decorator** (`function`):
    A decorator function that sets the skip parameters for the benchmark function.

    #### Notes
    The `skip_benchmark_for_params` decorator can be used to specify skip parameters
    for a benchmark function. The skip parameters define combinations of values that
    should be skipped when running the benchmark. The decorated function's `skip_params`
    attribute will be set with the provided skip parameters, which will be used during
    the benchmarking process.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "skip_params", skip_params_list)
        return wrapper

    return decorator


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

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(wrapper, "skip_benchmark", True)
    return wrapper


def skip_benchmark_if(condition):
    """
    Decorator to skip benchmarking of a function if a condition is met.

    #### Parameters
    **condition** (`bool`)
    : A boolean that indicates whether to skip benchmarking. If `True`,
      the decorated function will be skipped for benchmarking. If `False`,
      the decorated function will be benchmarked as usual.

    #### Returns
    **decorator** (function)
    : A decorator function that sets the condition under which the decorated function
      will be skipped for benchmarking.

    #### Notes
    The `skip_if` decorator can be used to skip the benchmarking of a specific function
    if a condition is met.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if condition:
            setattr(wrapper, "skip_benchmark", True)
        return wrapper

    return decorator


def skip_params_if(skip_params_list, condition):
    """
    Decorator to set skip parameters for a benchmark function if a condition is met.

    #### Parameters
    **skip_params_list** (`list`):
    A list specifying the skip parameters for the benchmark function.

    **condition** (`bool`)
    : A boolean that indicates whether to set the skip parameters. If `True`,
      the skip parameters will be set for the decorated function. If `False`,
      no parameters will be skipped.

    #### Returns
    **decorator** (function):
    A decorator function that sets the skip parameters for the benchmark function
      if the condition is met.

    #### Notes
    The `skip_params_if` decorator can be used to specify skip parameters for a
      benchmark function if a condition is met.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if condition:
            setattr(wrapper, "skip_params", skip_params_list)
        return wrapper

    return decorator


__all__ = ["skip_for_params", "skip_benchmark", "skip_benchmark_if", "skip_params_if"]
