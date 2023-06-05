import json
import os
import struct
import sys
import tempfile
import time
import timeit

from .aux import posix_redirect_output, update_sys_path
from .discovery import disc_benchmarks
from .run import _run

wall_timer = timeit.default_timer


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
                "did not receive data from socket " f"(size {size}, got only {data !r})"
            )
    return data


def _run_server(args):
    import signal
    import socket

    (
        benchmark_dir,
        socket_name,
    ) = args

    update_sys_path(benchmark_dir)

    # Socket I/O
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(socket_name)
    s.listen(1)

    # Read and act on commands from socket
    while True:
        stdout_file = None

        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            break

        try:
            fd, stdout_file = tempfile.mkstemp()
            os.close(fd)

            # Read command
            (read_size,) = struct.unpack("<Q", recvall(conn, 8))
            command_text = recvall(conn, read_size)
            command_text = command_text.decode("utf-8")

            # Parse command
            command = json.loads(command_text)
            action = command.pop("action")

            if action == "quit":
                break
            elif action == "preimport":
                # Import benchmark suite before forking.
                # Capture I/O to a file during import.
                with posix_redirect_output(stdout_file, permanent=False):
                    for benchmark in disc_benchmarks(
                        benchmark_dir, ignore_import_errors=True
                    ):
                        pass

                # Report result
                with open(stdout_file, errors="replace") as f:
                    out = f.read()
                out = json.dumps(out)
                out = out.encode("utf-8")
                conn.sendall(struct.pack("<Q", len(out)))
                conn.sendall(out)
                continue

            benchmark_id = command.pop("benchmark_id")
            params_str = command.pop("params_str")
            profile_path = command.pop("profile_path")
            result_file = command.pop("result_file")
            timeout = command.pop("timeout")
            cwd = command.pop("cwd")

            if command:
                raise RuntimeError(f"Command contained unknown data: {command_text !r}")

            # Spawn benchmark
            run_args = (
                benchmark_dir,
                benchmark_id,
                params_str,
                profile_path,
                result_file,
            )
            pid = os.fork()
            if pid == 0:
                conn.close()
                sys.stdin.close()
                exitcode = 1
                try:
                    with posix_redirect_output(stdout_file, permanent=True):
                        try:
                            os.chdir(cwd)
                            _run(run_args)
                            exitcode = 0
                        except BaseException:
                            import traceback

                            traceback.print_exc()
                finally:
                    os._exit(exitcode)

            # Wait for results
            # (Poll in a loop is simplest --- also used by subprocess.py)
            start_time = wall_timer()
            is_timeout = False
            time2sleep = 1e-15
            while True:
                res, status = os.waitpid(pid, os.WNOHANG)
                if res != 0:
                    break

                if timeout is not None and wall_timer() > start_time + timeout:
                    # Timeout
                    if is_timeout:
                        os.kill(pid, signal.SIGKILL)
                    else:
                        os.kill(pid, signal.SIGTERM)
                    is_timeout = True
                time2sleep *= 1e1
                time.sleep(min(time2sleep, 0.001))

            # Report result
            with open(stdout_file, errors="replace") as f:
                out = f.read()

            # Emulate subprocess
            if os.WIFSIGNALED(status):
                retcode = -os.WTERMSIG(status)
            elif os.WIFEXITED(status):
                retcode = os.WEXITSTATUS(status)
            elif os.WIFSTOPPED(status):
                retcode = -os.WSTOPSIG(status)
            else:
                # shouldn't happen, but fail silently
                retcode = -128

            info = {"out": out, "errcode": -256 if is_timeout else retcode}

            result_text = json.dumps(info)
            result_text = result_text.encode("utf-8")

            conn.sendall(struct.pack("<Q", len(result_text)))
            conn.sendall(result_text)
        except KeyboardInterrupt:
            break
        finally:
            conn.close()
            if stdout_file is not None:
                os.unlink(stdout_file)
