# About [![Documentation](https://img.shields.io/badge/Documentation-latest-brightgreen?style=for-the-badge)](https://asv.readthedocs.io/projects/asv-runner/en/latest/)


Core Python benchmark code for `asv`.

**This package shall not have any dependencies on external packages and must be
compatible with all Python versions greater than or equal to `3.7`.**


For other functionality, refer to the `asv` package or consider writing an extension.

# Contributions

All contributions are welcome, this includes code and documentation
contributions but also questions or other clarifications. Note that we expect
all contributors to follow our [Code of
Conduct](https://github.com/airspeed-velocity/asv_runner/blob/main/CODE_OF_CONDUCT.md).

## Developing locally

A `pre-commit` job is setup on CI to enforce consistent styles, so it is best to
set it up locally as well (using [pipx](https://pypa.github.io/pipx/) for isolation):

```sh
# Run before commiting
pipx run pre-commit run --all-files
# Or install the git hook to enforce this
pipx run pre-commit install
```
