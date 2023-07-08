from functools import wraps

def skip_benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(wrapper, "skip_benchmark", True)
    return wrapper
