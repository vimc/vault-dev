"""Support for finding and installing the vault binary.

Use of this package requires that you have vault installed and
available.  It is only a single binary, so not very hard to install,
but the package will be used in situations where we don't want to
think about this too much.

If the environment variable `$VAULT_DEV_BIN_PATH` is set, then this is
preferred (and if vault is not found here an error is thrown).  This
can be the full path to the vault binary (include `.exe` on windows)
or to the directory in which `vault` or `vault.exe` is found.

If vault is present on `$PATH` we will use that.

We provide some support for downloading and installing vault, by
passing `install=True` to `ensure_installed()`.

If using GitHub actions, you can use an action
(e.g. `eLco/setup-vault`) to do this.

"""

import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests


def vault_path(*, required: bool = True) -> Path | None:
    """Compute path to vault binary

    Args:
        required: Throw if vault is not found

    Returns: The path to the vault binary, or `None` if not found, and
        if `required` is `False`.

    """
    if path := _find_vault_environ():
        return path
    if path := _find_vault_system():
        return path
    if required:
        msg = "vault not found"
        raise Exception(msg)
    return None


def ensure_installed(*, install: bool = False) -> None:
    """Ensure that vault is installed.

    Args:
        install: Install vault if not found?  If not already installed
            and if `install` is `False`, this function will throw.

    Returns:
        Nothing, called for side effects only.

    """
    path = vault_path(required=install)
    if path:
        print(f"Found vault at '{path}'")
    if not path:
        print("Did not find system vault, installing one for tests")
        path = _vault_install_session()
        print(f"Using vault at '{path}'")


def vault_download(dest: str | Path, version: str, platform: str) -> Path:
    """Download vault.

    Args:
        dest: Destination directory
        version: The version to download
        platform: The platform to download (`linux`, `windows` or `darwin`)

    Returns: The full path to the downloaded binary.
    """
    filename = _vault_exe_filename(platform)
    dest_bin = Path(dest) / filename
    if not dest_bin.exists():
        print(f"installing vault to '{dest}'")
        url = _vault_url(version, platform)
        data = requests.get(url, timeout=600).content
        with tempfile.TemporaryFile() as tmp:
            tmp.write(data)
            tmp.seek(0)
            z = zipfile.ZipFile(tmp)
            z.extract(filename, dest)
        os.chmod(dest_bin, 0o755)  # noqa S103
    return dest_bin


def _find_vault_environ() -> Path | None:
    path = os.environ.get("VAULT_DEV_BIN_PATH")
    if not path:
        return None
    ret = Path(path)
    if not ret.exists():
        msg = "VAULT_DEV_BIN_PATH is set, but does not exist"
        raise Exception(msg)
    if ret.is_dir():
        filename = _vault_exe_filename(_vault_platform())
        ret = ret / filename
        if not ret.exists():
            msg = f"{filename} not found at {ret}, from VAULT_DEV_BIN_PATH"
            raise Exception(msg)
    return ret


def _find_vault_system() -> Path | None:
    if path := shutil.which("vault"):
        return Path(path)
    else:
        return None


def _vault_exe_filename(platform: str) -> str:
    """Filename for the vault binary.

    Args:
        platform: The platform `windows`, `linux` or `darwin`

    Returns:
        The name of the vault binary (either `vault.exe` or `vault`)
    """
    return "vault.exe" if platform == "windows" else "vault"


def _vault_url(version: str, platform: str, arch: str = "amd64") -> str:
    base = "https://releases.hashicorp.com/vault"
    return f"{base}/{version}/vault_{version}_{platform}_{arch}.zip"


def _vault_platform() -> str:
    return platform.system().lower()


def _vault_install_session() -> Path:
    tmp = tempfile.TemporaryDirectory(delete=False)
    path = vault_download(tmp.name, "1.0.0", _vault_platform())
    os.environ["VAULT_DEV_BIN_PATH"] = str(path)
    return path
