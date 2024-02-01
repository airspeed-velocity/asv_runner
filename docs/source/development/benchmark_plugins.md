# Developing benchmarks

All benchmark plugins must follow a strict hierarchy:

- The package name must begin with `asv_bench`.
- Benchmark classes are defined in a `benchmarks` folder under the package module.
- Each exported new benchmark type has the `export_as_benchmark = [NAMEBenchmark]` attribute.

For more conventions, see the internally defined benchmark types within `asv_runner`.
