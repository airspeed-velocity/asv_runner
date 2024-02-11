# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/twisted/my-project/tree/main/changelog.d/>.

<!-- towncrier release notes start -->

## [0.2.1](https://github.com/airspeed-velocity/asv_runner/tree/0.2.1) - 11-02-2024


No significant changes.


## [0.2.0](https://github.com/airspeed-velocity/asv_runner/tree/0.2.0) - 11-02-2024


### Other Changes and Additions

- `asv_runner` now uses `towncrier` to manage the changelog, also adds the
  changeglog to the generated documentation.
  ([#38](https://github.com/airspeed-velocity/asv_runner/issues/38))
- The lowest supported version of `python` for building the `asv_runner`
  documentation is now `3.8`, since `3.7` has been EOL for [many months
now](https://endoflife.date/python).
([#39](https://github.com/airspeed-velocity/asv_runner/issues/39))


## [0.1.0](https://github.com/airspeed-velocity/asv_runner/tree/0.1.0) - 11-09-2023


### Bug Fixes

- Default `max_time` is set to `60.0` seconds to fix `--quick`.
  ([#29](https://github.com/airspeed-velocity/asv_runner/issues/29))
- `asv` will not try to access a missing `colorama` attribute.
  ([#32](https://github.com/airspeed-velocity/asv_runner/issues/32))

### Other Changes and Additions

- `pip-tools` and `pip-compile` are used to pin transitive dependencies for
  read the docs.
  ([#31](https://github.com/airspeed-velocity/asv_runner/issues/31))


## [0.0.9](https://github.com/airspeed-velocity/asv_runner/tree/0.0.9) - 20-08-2023


### New Features

- Adds a `skip_benchmark` decorator.

```python
from asv_runner.benchmarks.helpers import skip_benchmark

@skip_benchmark
class TimeSuite:
    """
    An example benchmark that times the performance of various kinds
    of iterating over dictionaries in Python.
    """
    def setup(self):
        self.d = {}
        for x in range(500):
            self.d[x] = None

    def time_keys(self):
        for key in self.d.keys():
            pass

    def time_values(self):
        for value in self.d.values():
            pass

    def time_range(self):
        d = self.d
        for key in range(500):
            d[key]
```

Usage requires `asv 0.6.0`.
([#13](https://github.com/airspeed-velocity/asv_runner/issues/13))
- Finely grained `skip_benchmark_if` and `skip_params_if` have been added.

```python
from asv_runner.benchmarks.mark import skip_benchmark_if, skip_params_if
import datetime

class TimeSuite:
    """
    An example benchmark that times the performance of various kinds
    of iterating over dictionaries in Python.
    """
    params = [100, 200, 300, 400, 500]
    param_names = ["size"]

    def setup(self, size):
        self.d = {}
        for x in range(size):
            self.d[x] = None

    @skip_benchmark_if(datetime.datetime.now().hour >= 12)
    def time_keys(self, size):
        for key in self.d.keys():
            pass

    @skip_benchmark_if(datetime.datetime.now().hour >= 12)
    def time_values(self, size):
        for value in self.d.values():
            pass

    @skip_benchmark_if(datetime.datetime.now().hour >= 12)
    def time_range(self, size):
        d = self.d
        for key in range(size):
            d[key]

    # Skip benchmarking when size is either 100 or 200 and the current hour is
12 or later.
    @skip_params_if([(100,), (200,)],
                    datetime.datetime.now().hour >= 12)
    def time_dict_update(self, size):
        d = self.d
        for i in range(size):
            d[i] = i
```

Usage requires `asv 0.6.0`.
([#17](https://github.com/airspeed-velocity/asv_runner/issues/17))
- Benchmarks can now be parameterized using decorators.

```python
import numpy as np
from asv_runner.benchmarks.mark import parameterize

@parameterize({"n":[10, 100]})
def time_sort(n):
    np.sort(np.random.rand(n))

@parameterize({'n': [10, 100], 'func_name': ['range', 'arange']})
def time_ranges_multi(n, func_name):
    f = {'range': range, 'arange': np.arange}[func_name]
    for i in f(n):
        pass

@parameterize({"size": [10, 100, 200]})
class TimeSuiteDecoratorSingle:
    def setup(self, size):
        self.d = {}
        for x in range(size):
            self.d[x] = None

    def time_keys(self, size):
        for key in self.d.keys():
            pass

    def time_values(self, size):
        for value in self.d.values():
            pass

@parameterize({'n': [10, 100], 'func_name': ['range', 'arange']})
class TimeSuiteMultiDecorator:
    def time_ranges(self, n, func_name):
        f = {'range': range, 'arange': np.arange}[func_name]
        for i in f(n):
            pass
```

Usage requires `asv 0.6.0`.
([#18](https://github.com/airspeed-velocity/asv_runner/issues/18))
- Benchmarks can now be skipped during execution.

```python
from asv_runner.benchmarks.mark import skip_for_params, parameterize,
SkipNotImplemented

# Fast because no setup is called
class SimpleFast:
    params = ([False, True])
    param_names = ["ok"]

    @skip_for_params([(False, )])
    def time_failure(self, ok):
        if ok:
            x = 34.2**4.2

@parameterize({"ok": [False, True]})
class SimpleSlow:
    def time_failure(self, ok):
        if ok:
            x = 34.2**4.2
        else:
            raise SkipNotImplemented(f"{ok} is skipped")
```

Usage requires `asv 0.6.0`.
([#20](https://github.com/airspeed-velocity/asv_runner/issues/20))

### Bug Fixes

- It is possible to set a default timeout from `asv`.
  ([#19](https://github.com/airspeed-velocity/asv_runner/issues/19))

### Other Changes and Additions

- Documentation, both long-form and API level has been added.
  ([#6](https://github.com/airspeed-velocity/asv_runner/issues/6))
