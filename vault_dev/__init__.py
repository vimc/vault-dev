from vault_dev.server import server, VaultDevServerError
from vault_dev.install import ensure_installed

__all__ = [
    ensure_installed,
    server,
    VaultDevServerError
]
