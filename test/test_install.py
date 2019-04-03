import pytest
import tempfile

from vault_dev.install import *

def test_vault_exe_name_correct():
    assert vault_exe_filename("windows") == "vault.exe"
    assert vault_exe_filename("linux") == "vault"
    assert vault_exe_filename("darwin") == "vault"


def test_vault_download_skips_existing_file():
    platform = vault_platform()
    version = "1.0.0"
    with tempfile.TemporaryDirectory() as dest:
        p = "{}/{}".format(dest, vault_exe_filename(platform))
        open(p, "a").close()
        assert vault_download(dest, version, platform) == p
        assert os.path.getsize(p) == 0


def test_vault_download():
    with tempfile.TemporaryDirectory() as path:
        p = install(path)
        assert os.path.exists(p)


def test_cleanup():
    assert vault_dev_exe.exists()
    path = vault_dev_exe().vault(True)
    tmp = path + ".bak"
    shutil.copy(path, tmp)
    cleanup()
    assert not os.path.exists(path)
    assert not vault_dev_exe().exists()
    shutil.copy(tmp, path)
    assert vault_dev_exe().exists()


def test_error_with_no_suitable_vault():
    p = vault_dev_exe.exe
    vault_dev_exe.exe = "vault_missing"
    assert vault_dev_exe.vault(False) is None
    with pytest.raises(Exception, match="No vault found"):
        vault_dev_exe.vault(True)
    vault_dev_exe.exe = p
    assert vault_dev_exe.vault(True) == p
