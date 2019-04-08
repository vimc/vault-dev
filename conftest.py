import vault_dev.install

# https://stackoverflow.com/a/35394239
def pytest_sessionstart(session):
    """ before session.main() is called. """
    vault_dev.install.ensure_installed()
