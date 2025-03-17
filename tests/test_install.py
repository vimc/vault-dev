import os
import tempfile

import pytest

from vault_dev.install import (
    _vault_exe_filename,
    _vault_install_session,
    _vault_platform,
    vault_download,
    vault_path,
)
from vault_dev.utils import transient_envvars


def test_vault_exe_name_correct():
    assert _vault_exe_filename("windows") == "vault.exe"
    assert _vault_exe_filename("linux") == "vault"
    assert _vault_exe_filename("darwin") == "vault"


def test_vault_download_skips_existing_file(tmp_path):
    platform = _vault_platform()
    version = "1.0.0"
    p = tmp_path / _vault_exe_filename(platform)
    open(p, "a").close()
    assert vault_download(tmp_path, version, platform) == p
    assert os.path.getsize(p) == 0


@pytest.mark.internet
def test_vault_download(tmp_path):
    with transient_envvars({"VAULT_DEV_BIN_PATH": None}):
        path = _vault_install_session()
        assert path.exists()
        assert os.environ["VAULT_DEV_BIN_PATH"] == str(path)
        assert vault_path() == path
