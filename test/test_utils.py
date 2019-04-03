import os
import pytest
import shutil
import tempfile

from vault_dev.utils import *

def test_drop_envvar_removes_envvar():
    name = "VAULT_DEV_TEST_VAR"
    os.environ[name] = "x"
    drop_envvar(name)
    assert name not in os.environ


def test_drop_envvar_ignores_missing_envvar():
    name = "VAULT_DEV_TEST_VAR"
    drop_envvar(name)
    assert name not in os.environ


def test_find_executable():
    assert type(find_executable("ls", None)) == str
    with tempfile.NamedTemporaryFile() as f:
        p = find_executable("ls", f.name)
        assert p == f.name
    with pytest.raises(OSError, match="not found on path"):
        find_executable("asdfasdfasdaf", None)
    with pytest.raises(Exception, match="Path '/missing/path' does not exist"):
        find_executable("asdfasdfasdaf", "/missing/path")
