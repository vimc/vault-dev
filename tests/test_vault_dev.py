import os
import socket

import pytest

import vault_dev

vault_dev.ensure_installed()


def test_server_basic():
    s = vault_dev.Server()
    assert not s.is_running()
    s.start()
    assert s.is_running()
    assert s.url() == f"http://localhost:{s.port}"
    cl = s.client()
    # check that vault came up ok and that the v1 key-value store works
    cl.write("secret/foo", a="b")
    assert cl.read("secret/foo")["data"]["a"] == "b"
    s.stop()
    assert not s.is_running()


def test_that_enter_exit_works():
    with vault_dev.Server() as s:
        p = s.process
        assert s.is_running()
    assert p.poll()


def test_failure_to_start():
    with socket.socket() as s:
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        server = vault_dev.Server(port=port)
        with pytest.raises(vault_dev.VaultDevServerError) as e:
            server.start()
        assert e.value.msg == "Vault process has terminated"
        assert e.value.code is not None


def test_failure_after_start():
    with vault_dev.Server() as s:
        s.start()
        s.token = "root"
        with pytest.raises(vault_dev.VaultDevServerError) as e:
            s._wait_until_active(0.5, 0.1)
        assert e.value.msg == "Vault did not start in time"


def test_verbose_mode(capsys):
    with vault_dev.Server(verbose=True) as s:
        port = s.port
    captured = capsys.readouterr().out
    assert f"Starting vault server on port {port}" in captured
    assert "Waiting for server to become active" in captured
    assert "Connection made" in captured
    assert "Configuring old-style kv engine at /secret" in captured


def test_restart_is_not_an_error():
    with vault_dev.Server() as s:
        assert s.start() is None


def test_can_export_token_when_present():
    try:
        os.environ["VAULT_TOKEN"] = "previous"
        with vault_dev.Server(export_token=True) as s:
            assert os.environ["VAULT_TOKEN"] == s.token
        assert os.environ["VAULT_TOKEN"] == "previous"
    finally:
        del os.environ["VAULT_TOKEN"]


def test_can_export_token_when_not_present_already():
    del os.environ["VAULT_TOKEN"]
    with vault_dev.Server(export_token=True) as s:
        assert os.environ["VAULT_TOKEN"] == s.token
    assert "VAULT_TOKEN" not in os.environ
