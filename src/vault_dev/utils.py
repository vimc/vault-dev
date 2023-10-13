from contextlib import contextmanager
import os
import socket


def find_free_port():
    with socket.socket() as s:
        # Let the OS pick a random free port on our machine
        s.bind(("localhost", 0))
        # Then mark this port as immediately ready for reuse - see
        # https://docs.python.org/3.5/library/socket.html and search
        # for SO_REUSEADDR
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Return the port number itself (getsockname is tuple (name, port))
        return s.getsockname()[1]


def read_all_lines(con, prefix=""):
    output = []
    while True:
        d = con.readline()
        if not d:
            break
        output.append(prefix + d.decode("UTF-8"))
    return "".join(output)


@contextmanager
def transient_envvar(**kwargs):
    prev = {
        k: os.environ[k] if k in os.environ else None
        for k in kwargs.keys()
    }
    try:
        _setdictvals(kwargs, os.environ)
        yield
    finally:
        _setdictvals(prev, os.environ)


def _setdictvals(new, container):
    for k, v in new.items():
        if v is None:
            if k in container:
                del container[k]
        else:
            container[k] = v
    return container
