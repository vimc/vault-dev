import os

from vault_dev.utils import drop_envvar


def test_drop_envvar_removes_envvar():
    name = "VAULT_DEV_TEST_VAR"
    os.environ[name] = "x"
    drop_envvar(name)
    assert name not in os.environ


def test_drop_envvar_ignores_missing_envvar():
    name = "VAULT_DEV_TEST_VAR"
    drop_envvar(name)
    assert name not in os.environ
