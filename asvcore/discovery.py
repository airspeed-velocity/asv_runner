import importlib
import inspect
import json
import os
import pkgutil
import traceback

from .aux import update_sys_path
from .benchmarks import benchmark_types


def _get_benchmark(attr_name, module, klass, func):
    try:
        name = func.benchmark_name
    except AttributeError:
        name = None
        search = attr_name
    else:
        search = name.split(".")[-1]

    for cls in benchmark_types:
        if cls.name_regex.match(search):
            break
    else:
        return
    # relative to benchmark_dir
    mname_parts = module.__name__.split(".", 1)[1:]
    if klass is None:
        if name is None:
            name = ".".join(mname_parts + [func.__name__])
        sources = [func, module]
    else:
        instance = klass()
        func = getattr(instance, attr_name)
        if name is None:
            name = ".".join(mname_parts + [klass.__name__, attr_name])
        sources = [func, instance, module]
    return cls(name, func, sources)


def disc_modules(module_name, ignore_import_errors=False):
    """
    Recursively import a module and all sub-modules in the package

    Yields
    ------
    module
        Imported module in the package tree

    """
    if not ignore_import_errors:
        module = importlib.import_module(module_name)
    else:
        try:
            module = importlib.import_module(module_name)
        except BaseException:
            traceback.print_exc()
            return
    yield module

    if getattr(module, "__path__", None):
        for _, name, _ in pkgutil.iter_modules(module.__path__, module_name + "."):
            for item in disc_modules(name, ignore_import_errors):
                yield item


def disc_benchmarks(root, ignore_import_errors=False):
    """
    Discover all benchmarks in a given directory tree, yielding Benchmark
    objects

    For each class definition, looks for any methods with a
    special name.

    For each free function, yields all functions with a special
    name.
    """

    root_name = os.path.basename(root)

    for module in disc_modules(root_name, ignore_import_errors=ignore_import_errors):
        for attr_name, module_attr in (
            (k, v) for k, v in module.__dict__.items() if not k.startswith("_")
        ):
            if inspect.isclass(module_attr) and not inspect.isabstract(module_attr):
                for name, class_attr in inspect.getmembers(module_attr):
                    if inspect.isfunction(class_attr) or inspect.ismethod(class_attr):
                        benchmark = _get_benchmark(
                            name, module, module_attr, class_attr
                        )
                        if benchmark is not None:
                            yield benchmark
            elif inspect.isfunction(module_attr):
                benchmark = _get_benchmark(attr_name, module, None, module_attr)
                if benchmark is not None:
                    yield benchmark


def get_benchmark_from_name(root, name, extra_params=None):
    """
    Create a benchmark from a fully-qualified benchmark name.

    Parameters
    ----------
    root : str
        Path to the root of a benchmark suite.

    name : str
        Fully-qualified name to a specific benchmark.
    """

    if "-" in name:
        try:
            name, param_idx = name.split("-", 1)
            param_idx = int(param_idx)
        except ValueError:
            raise ValueError(f"Benchmark id {name!r} is invalid")
    else:
        param_idx = None

    update_sys_path(root)
    benchmark = None

    # try to directly import benchmark function by guessing its import module
    # name
    parts = name.split(".")
    for i in [1, 2]:
        path = os.path.join(root, *parts[:-i]) + ".py"
        if not os.path.isfile(path):
            continue
        modname = ".".join([os.path.basename(root)] + parts[:-i])
        module = importlib.import_module(modname)
        try:
            module_attr = getattr(module, parts[-i])
        except AttributeError:
            break
        if i == 1 and inspect.isfunction(module_attr):
            benchmark = _get_benchmark(parts[-i], module, None, module_attr)
            break
        elif i == 2 and inspect.isclass(module_attr):
            try:
                class_attr = getattr(module_attr, parts[-1])
            except AttributeError:
                break
            if inspect.isfunction(class_attr) or inspect.ismethod(class_attr):
                benchmark = _get_benchmark(parts[-1], module, module_attr, class_attr)
                break

    if benchmark is None:
        for benchmark in disc_benchmarks(root):
            if benchmark.name == name:
                break
        else:
            raise ValueError(f"Could not find benchmark '{name}'")

    if param_idx is not None:
        benchmark.set_param_idx(param_idx)

    if extra_params:

        class ExtraBenchmarkAttrs:
            pass

        for key, value in extra_params.items():
            setattr(ExtraBenchmarkAttrs, key, value)
        benchmark._attr_sources.insert(0, ExtraBenchmarkAttrs)

    return benchmark


def list_benchmarks(root, fp):
    """
    List all of the discovered benchmarks to fp as JSON.
    """
    update_sys_path(root)

    # Streaming of JSON back out to the master process

    fp.write("[")
    first = True
    for benchmark in disc_benchmarks(root):
        if not first:
            fp.write(", ")
        clean = dict(
            (k, v)
            for (k, v) in benchmark.__dict__.items()
            if isinstance(v, (str, int, float, list, dict, bool))
            and not k.startswith("_")
        )
        json.dump(clean, fp, skipkeys=True)
        first = False
    fp.write("]")


def _discover(args):
    benchmark_dir, result_file = args
    with open(result_file, "w") as fp:
        list_benchmarks(benchmark_dir, fp)
