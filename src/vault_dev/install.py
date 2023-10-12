## This whole file struggles with the problem of installing a global
## resource that is somewhat expensive (a vault binary, needed for
## installing tests) and we want to just use a system binary if it's
## already found.
##
## The only entrypoint that other packages need to be concerned with
## is "ensure_installed()" which can be run with no arguments and
## ensures that a suitable vault binary is installed.
##
## This package then uses the "vault_path()" function to get the path
## to either the system vault or the one that was installed.
import os
import platform
import shutil
import tempfile
import zipfile

import requests


def ensure_installed():
    if not shutil.which("vault"):
        print("Did not find system vault, installing one for tests")
        global_vault_dev_exe.install()


def vault_path():
    vault = shutil.which("vault")
    if not vault:
        vault = global_vault_dev_exe.vault()
    return vault


def vault_exe_filename(platform):
    if platform == "windows":
        return "vault.exe"
    else:
        return "vault"


def vault_url(version, platform, arch="amd64"):
    fmt = "https://releases.hashicorp.com/vault/{}/vault_{}_{}_{}.zip"
    return fmt.format(version, version, platform, arch)


def vault_platform():
    return platform.system().lower()


def vault_download(dest, version, platform):
    dest_bin = f"{dest}/{vault_exe_filename(platform)}"
    if not os.path.exists(dest_bin):
        print(f"installing vault to '{dest}'")
        url = vault_url(version, platform)
        data = requests.get(url, timeout=600).content
        with tempfile.TemporaryFile() as tmp:
            tmp.write(data)
            tmp.seek(0)
            z = zipfile.ZipFile(tmp)
            z.extract(vault_exe_filename(platform), dest)
        os.chmod(dest_bin, 0o755)  # noqa S103
    return dest_bin


class VaultDevExe:
    path = None
    exe = None

    def __init__(self):
        if not self.path:
            tmp = tempfile.TemporaryDirectory()
            exe = vault_exe_filename(vault_platform())
            self.path = tmp
            self.exe = f"{tmp.name}/{exe}"

    def install(self):
        return vault_download(self.path.name, "1.0.0", vault_platform())

    def exists(self):
        return self.exe and os.path.exists(self.exe)

    def vault(self):
        if self.exists():
            return self.exe
        else:
            msg = "No vault found"
            raise Exception(msg)


# Package/module global used so that we only install vault once per
# session.
global_vault_dev_exe = VaultDevExe()
