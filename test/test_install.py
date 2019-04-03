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


def test_dev_directory_does_not_change():
    p1 = vault_dev_directory()
    p2 = vault_dev_directory()
    assert str(p1) == str(p2)
    assert repr(p1) == repr(p2)
