import gc
import socket
import pytest

import vault_dev
from vault_dev.utils import *

def test_server_basic():
    s = vault_dev.server()
    assert not s.is_running()
    s.start()
    assert s.is_running()
    cl = s.client()
    ## check that vault came up ok and that the v1 key-value store works
    cl.write("secret/foo", a="b")
    assert cl.read("secret/foo")["data"]["a"] == "b"
    s.stop()
    assert not s.is_running()


def test_that_enter_exit_works():
    with vault_dev.server() as s:
        p = s.process
        assert s.is_running()
    assert p.poll()


def test_failure_to_start():
    with socket.socket() as s:
        s.bind(('localhost', 0))
        port = s.getsockname()[1]
        server = vault_dev.server(port)
        with pytest.raises(vault_dev.VaultDevServerError) as e:
            server.start()
            assert e.message == "Vault process has terminated"
            assert e.code is not None


def test_faiure_after_start():
    with vault_dev.server() as s:
        s.start()
        s.token = "root"
        with pytest.raises(vault_dev.VaultDevServerError) as e:
            s._wait_until_active(0.5, 0.1)
            assert e.message == "Vault did not start in time"
            assert e.code is None
            assert e.stdout[0].startswith(">> ")


def test_verbose_mode(capsys):
    with vault_dev.server(verbose=True) as s:
        port = s.port
    captured = capsys.readouterr().out
    assert "Starting vault server on port {}".format(port) in captured
    assert "Waiting for server to become active" in captured
    assert "Connection made" in captured
    assert "Configuring old-style kv engine at /secret" in captured


def test_restart_is_not_an_error():
    with vault_dev.server() as s:
        assert s.start() is None


def test_cleanup_on_gc():
    def f():
        s = vault_dev.server()
        s.start()
        return s.process
    p = f()
    gc.collect()
    assert p.poll() < 0
