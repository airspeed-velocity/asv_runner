import contextlib
import importlib
import os
import sys
import tempfile

from .benchmarks._maxrss import set_cpu_affinity


class SpecificImporter:
    """
    Module importer that only allows loading a given module from the
    given path.

    Using this enables importing the asv benchmark suite without
    adding its parent directory to sys.path. The parent directory can
    in principle contain anything, including some version of the
    project module (common situation if asv.conf.json is on project
    repository top level).
    """

    def __init__(self, name, root):
        self._name = name
        self._root = root

    def find_spec(self, fullname, path, target):
        if fullname == self._name:
            if path is not None:
                raise ValueError()
            finder = importlib.machinery.PathFinder()
            return finder.find_spec(fullname, [self._root], target)
        return None


def update_sys_path(root):
    sys.meta_path.insert(
        0, SpecificImporter(os.path.basename(root), os.path.dirname(root))
    )


@contextlib.contextmanager
def posix_redirect_output(filename=None, permanent=True):
    """
    Redirect stdout/stderr to a file, using posix dup2.
    """
    sys.stdout.flush()
    sys.stderr.flush()

    stdout_fd = sys.stdout.fileno()
    stderr_fd = sys.stderr.fileno()

    if not permanent:
        stdout_fd_copy = os.dup(stdout_fd)
        stderr_fd_copy = os.dup(stderr_fd)

    if filename is None:
        out_fd, filename = tempfile.mkstemp()
    else:
        out_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

    try:
        # Redirect stdout and stderr to file
        os.dup2(out_fd, stdout_fd)
        os.dup2(out_fd, stderr_fd)

        yield filename
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.close(out_fd)

        if not permanent:
            os.dup2(stdout_fd_copy, stdout_fd)
            os.dup2(stderr_fd_copy, stderr_fd)
            os.close(stdout_fd_copy)
            os.close(stderr_fd_copy)


def recvall(sock, size):
    """
    Receive data of given size from a socket connection
    """
    data = b""
    while len(data) < size:
        s = sock.recv(size - len(data))
        data += s
        if not s:
            raise RuntimeError(
                "did not receive data from socket "
                "(size {}, got only {!r})".format(size, data)
            )
    return data


def set_cpu_affinity_from_params(extra_params):
    affinity_list = extra_params.get("cpu_affinity", None)
    if affinity_list is not None:
        try:
            set_cpu_affinity(affinity_list)
        except BaseException as exc:
            print(f"asv: setting cpu affinity {affinity_list !r} failed: {exc !r}")
