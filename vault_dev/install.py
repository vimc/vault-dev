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
        vault_dev_exe().install()


def cleanup():
    vault_dev_exe().cleanup()


## Order of things:
##
## 1. given path
## 2. vault on the system path
## 3. vault installed by our package
## 4. error
def vault_path(path):
    try:
        vault = find_executable("vault", path)
    except OSError as e:
        vault = vault_dev_exe.vault(True)
    return vault


def install(dest, version="1.0.0", platform=None):
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


class vault_dev_exe:
    path = None
    exe = None
    def __init__(self):
        if not self.path:
            tmp = tempfile.TemporaryDirectory()
            exe = vault_exe_filename(vault_platform())
            vault_dev_exe.path = tmp
            vault_dev_exe.exe = "{}/{}".format(tmp.name, exe)

    def cleanup(self):
        p = vault_dev_exe.exe
        if os.path.exists(p):
            print("Cleaning up the vault directory - removing {}".format(p))
            os.remove(p)

    def install(self):
        return install(self.path.name)

    @staticmethod
    def exists():
        return vault_dev_exe.exe and os.path.exists(vault_dev_exe.exe)

    @staticmethod
    def vault(required):
        if vault_dev_exe.exists():
            return vault_dev_exe.exe
        elif not required:
            return None
        else:
            raise Exception("No vault found")
