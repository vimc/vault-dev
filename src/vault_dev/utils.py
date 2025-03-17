import os
import socket
from collections.abc import Iterator
from contextlib import contextmanager


def find_free_port() -> int:
    with socket.socket() as s:
        # Let the OS pick a random free port on our machine
        s.bind(("localhost", 0))
        # Then mark this port as immediately ready for reuse - see
        # https://docs.python.org/3.5/library/socket.html and search
        # for SO_REUSEADDR
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Return the port number itself (getsockname is tuple (name, port))
        return s.getsockname()[1]


def read_all_lines(con, prefix="") -> str:
    output = []
    while True:
        d = con.readline()
        if not d:
            break
        output.append(prefix + d.decode("UTF-8"))
    return "".join(output)


@contextmanager
def transient_envvars(env: dict[str, str | None]) -> Iterator[None]:
    def _set_envvars(env):
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    prev = {k: os.environ.get(k) for k in env.keys()}
    try:
        _set_envvars(env)
        yield
    finally:
        _set_envvars(prev)
