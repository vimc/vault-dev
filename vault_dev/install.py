import os
import platform
import requests
import shutil
import tempfile
import zipfile

from vault_dev.utils import find_executable


def ensure_installed():
    if not shutil.which("vault"):
        print("Did not find system vault, installing one for tests")
        install()


def cleanup():
    if vault_dev_directory.path and os.path.exists(vault_dev_directory.path):
        print("\nCleaning up the vault directory")
        shutil.rmtree(vault_dev_directory.path)
        vault_dev_directory.path = None


def vault_path(path):
    try:
        vault = find_executable("vault", path)
    except OSError as e:
        vault_exe = vault_exe_filename(vault_platform())
        vault = "{}/{}".format(vault_dev_directory(), vault_exe)
        if not os.path.exists(vault):
            raise e
    return vault


def install(dest=None, version="1.0.0", platform=None):
    if not dest:
        dest = vault_dev_directory().path
    return vault_download(dest, version, platform or vault_platform())


def vault_exe_filename(platform):
    if platform == "windows":
        return "vault.exe"
    else:
        return "vault"


def vault_url(version, platform, arch = "amd64"):
    fmt = "https://releases.hashicorp.com/vault/{}/vault_{}_{}_{}.zip"
    return fmt.format(version, version, platform, arch)


def vault_platform():
    return platform.system().lower()


def vault_download(dest, version, platform):
    dest_bin = "{}/{}".format(dest, vault_exe_filename(platform))
    if not os.path.exists(dest_bin):
        print("installing vault to '{}'".format(dest))
        url = vault_url(version, platform)
        data = requests.get(url).content
        with tempfile.TemporaryFile() as tmp:
            tmp.write(data)
            tmp.seek(0)
            z = zipfile.ZipFile(tmp)
            z.extract(vault_exe_filename(platform), dest)
        os.chmod(dest_bin, 0o755)
    return dest_bin


class vault_dev_directory:
    path = None
    def __init__(self):
        if not self.path:
            vault_dev_directory.path = tempfile.TemporaryDirectory().name
    def __repr__(self):
        return str(self.path)
