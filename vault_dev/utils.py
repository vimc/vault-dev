import socket
import errno


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


def port_is_in_use(port):
    with socket.socket() as s:
        try:
            s.bind(("127.0.0.1", port))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return False
        except socket.error as e:
            return e.errno == errno.EADDRINUSE
