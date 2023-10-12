import os
import tempfile

import pytest

from vault_dev.install import (
    VaultDevExe,
    vault_download,
    vault_exe_filename,
    vault_platform,
)


def test_vault_exe_name_correct():
    assert vault_exe_filename("windows") == "vault.exe"
    assert vault_exe_filename("linux") == "vault"
    assert vault_exe_filename("darwin") == "vault"


def test_vault_download_skips_existing_file():
    platform = vault_platform()
    version = "1.0.0"
    with tempfile.TemporaryDirectory() as dest:
        p = f"{dest}/{vault_exe_filename(platform)}"
        open(p, "a").close()
        assert vault_download(dest, version, platform) == p
        assert os.path.getsize(p) == 0


def test_vault_download():
    v = VaultDevExe()
    p = v.install()
    assert os.path.exists(p)
    assert v.vault() == p


def test_error_with_no_suitable_vault():
    v = VaultDevExe()
    with pytest.raises(Exception, match="No vault found"):
        v.vault()
