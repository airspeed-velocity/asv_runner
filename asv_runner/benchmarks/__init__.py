"""
Automatically discovers and imports benchmark classes from all submodules in
the current package.

#### Variables
**pkgname** (`str`)
: The name of the current package.

**pkgpath** (`_frozen_importlib_external._NamespacePath`)
: The path of the current package.

**module_names** (`List[str]`)
: The names of all submodules in the current package that don't contain an underscore.

**benchmark_types** (`List[Type]`)
: A list to hold all benchmark classes from the submodules.

#### Raises
**NotRequired** (`Exception`)
: If a submodule raises a `NotRequired` exception during import, it is ignored.

#### Notes
This module first identifies all submodules in the current package that don't contain
an underscore in their names. It then iterates over these submodules, imports each one,
and checks if it contains an attribute named "export_as_benchmark".

If such an attribute exists, its contents (which should be a list of benchmark classes)
are added to the `benchmark_types` list. If a submodule raises a `NotRequired` exception
during the import, it is ignored, and the loop continues with the next submodule.

This code is useful in a benchmarking suite where new benchmarks can be added simply by
adding a new submodule with an "export_as_benchmark" attribute.
"""

import importlib
import pkgutil

from ._exceptions import NotRequired

pkgname = __name__
pkgpath = __path__

module_names = [name for _, name, _ in pkgutil.iter_modules(pkgpath) if "_" not in name]
benchmark_types = []

for module_name in module_names:
    try:
        module = importlib.import_module(f"{pkgname}.{module_name}")
        if "export_as_benchmark" in dir(module):
            for bench in getattr(module, "export_as_benchmark"):
                benchmark_types.append(bench)
    except NotRequired:
        # Ignored.
        pass
