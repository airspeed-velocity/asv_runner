import importlib
import pkgutil

from ._exceptions import NotRequired

pkgname = __name__
pkgpath = __path__
module_names = [name for _, name, _ in pkgutil.iter_modules(pkgpath) if "_" not in name]

# Import all exported benchmark classes from the modules
benchmark_types = []
for module_name in module_names:
    try:
        module = importlib.import_module(f"{pkgname}.{module_name}")
        if "export_as_benchmark" in dir(module):
            for bench in getattr(module, "export_as_benchmark"):
                benchmark_types.append(bench)
    except NotRequired:
        pass
