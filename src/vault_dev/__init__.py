from deprecated import deprecated

from vault_dev.install import ensure_installed
from vault_dev.server import Server, VaultDevServerError


@deprecated("Please use 'Server', not 'server'")
class server(Server):
    pass


__all__ = ["Server", "VaultDevServerError", "server", "ensure_installed"]
