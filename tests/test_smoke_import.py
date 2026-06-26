"""Smoke tests shipped with CI-only PRs (no behavior change to the package)."""

from __future__ import print_function

import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "asv_runner"


class TestSmokeImport(unittest.TestCase):
    def test_import_package(self):
        import asv_runner  # noqa: F401

    def test_import_public_entrypoint_modules(self):
        # Subprocess CLI surface used by asv.benchmark
        import asv_runner.check  # noqa: F401
        import asv_runner.discovery  # noqa: F401
        import asv_runner.run  # noqa: F401
        import asv_runner.server  # noqa: F401
        import asv_runner.setup_cache  # noqa: F401
        import asv_runner.timing  # noqa: F401

    def test_package_is_py37_syntax(self):
        # Static gate: no 3.8+ syntax nodes in runtime package.
        for path in sorted(PKG.rglob("*.py")):
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(path))
            for node in ast.walk(tree):
                name = type(node).__name__
                self.assertNotEqual(name, "NamedExpr", msg=str(path))
                self.assertNotEqual(name, "Match", msg=str(path))
            # feature_version is 3.8+ on the AST API; still validates parse on host
            ast.parse(src, feature_version=(3, 7))


if __name__ == "__main__":
    unittest.main()
