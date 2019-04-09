import errno
import os
import shutil
import socket


def find_free_port():
    with socket.socket() as s:
        # Let the OS pick a random free port on our machine
        s.bind(('localhost', 0))
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


def drop_envvar(name):
    if name in os.environ:
        del os.environ[name]
