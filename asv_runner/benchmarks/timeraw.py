import os
import re
import subprocess
import sys
import textwrap

from ._base import _get_first_attr, code_fingerprint
from .time import TimeBenchmark


def _normalize_timeraw_env(env):
    """
    Normalize a timeraw ``env`` mapping once (load time).

    #### Parameters
    **env** (`dict` or `None`)
    : Extra environment variables for the timed subprocess, or ``None``.

    #### Returns
    **out** (`dict` or `None`)
    : Mapping of ``str`` keys to ``str`` values, or ``None`` if unused/empty.

    #### Raises
    **TypeError**
    : If ``env`` is not a ``dict``, or any value is ``None`` (cannot be a real
    env entry; refusing to coerce to the string ``"None"``).
    """
    if env is None:
        return None
    if not isinstance(env, dict):
        raise TypeError(
            "timeraw benchmark attribute 'env' must be a dict, got %r" % (type(env),)
        )
    if not env:
        return None
    out = {}
    for key, value in env.items():
        if value is None:
            raise TypeError(
                "timeraw env values must not be None (key %r); omit the key instead"
                % (key,)
            )
        out[str(key)] = str(value)
    return out


def _env_fingerprint(env):
    """Stable string for incorporating ``env`` into benchmark version identity."""
    if not env:
        return ""
    parts = ["%s=%s" % (k, env[k]) for k in sorted(env)]
    return "\n".join(parts)


class _SeparateProcessTimer:
    """
    Timer that runs a statement in a separate Python process via ``timeit``.

    **env** must already be normalized (or ``None``); not re-validated here.
    """

    subprocess_tmpl = textwrap.dedent(
        '''
        from __future__ import print_function
        from timeit import timeit, default_timer as timer
        print(repr(timeit(stmt="""{stmt}""", setup="""{setup}""",
                    number={number}, timer=timer)))
    '''
    ).strip()

    def __init__(self, func, env=None):
        self.func = func
        self.env = env

    def _child_environ(self):
        """Explicit child environ: parent mapping plus optional overrides."""
        child = dict(os.environ)
        if self.env:
            child.update(self.env)
        return child

    def timeit(self, number):
        stmt = self.func()
        if isinstance(stmt, tuple):
            stmt, setup = stmt
        else:
            setup = ""
        stmt = textwrap.dedent(stmt)
        setup = textwrap.dedent(setup)
        stmt = stmt.replace(r'"""', r"\"\"\"")
        setup = setup.replace(r'"""', r"\"\"\"")

        code = self.subprocess_tmpl.format(stmt=stmt, setup=setup, number=number)

        evaler = textwrap.dedent(
            """
            import sys
            code = sys.stdin.read()
            exec(code)
            """
        )

        proc = subprocess.Popen(
            [sys.executable, "-c", evaler],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._child_environ(),
        )
        stdout, stderr = proc.communicate(input=code.encode("utf-8"))
        if proc.returncode != 0:
            raise RuntimeError("Subprocess failed: %s" % (stderr.decode(),))

        return float(stdout.decode("utf-8").strip())


class TimerawBenchmark(TimeBenchmark):
    """
    Timing benchmark executed once per sample in a separate process.

    Set ``env = {"KEY": "value"}`` on the function or class (or use
    ``@benchmark(env={...})``) to inject variables into the **timed** child
    (airspeed-velocity/asv#1471). Default ``version`` includes a fingerprint of
    that mapping so env-only changes invalidate results.
    """

    name_regex = re.compile("^(Timeraw[A-Z_].+)|(timeraw_.+)$")

    def __init__(self, name, func, attr_sources):
        TimeBenchmark.__init__(self, name, func, attr_sources)
        explicit_version = _get_first_attr(attr_sources, "version", None)
        if explicit_version is None:
            env_fp = _env_fingerprint(
                _normalize_timeraw_env(_get_first_attr(attr_sources, "env", None))
            )
            if env_fp:
                self.version = code_fingerprint(
                    self.code + "\n# timeraw_env\n" + env_fp
                )

    def _load_vars(self):
        TimeBenchmark._load_vars(self)
        self.number = int(_get_first_attr(self._attr_sources, "number", 1))
        self._timeraw_env = _normalize_timeraw_env(
            _get_first_attr(self._attr_sources, "env", None)
        )
        del self.timer

    def _get_timer(self, *param):
        if param:

            def func():
                return self.func(*param)

        else:
            func = self.func
        return _SeparateProcessTimer(func, env=self._timeraw_env)

    def do_profile(self, filename=None):
        raise ValueError("Raw timing benchmarks cannot be profiled")


export_as_benchmark = [TimerawBenchmark]
