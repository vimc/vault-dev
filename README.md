# vault-dev

[![PyPI - Version](https://img.shields.io/pypi/v/vault-dev.svg)](https://pypi.org/project/vault-dev)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vault-dev.svg)](https://pypi.org/project/vault-dev)

Use vault server in development mode in tests, from python

## Installation:

Install with pip

``` shell
pip3 install --user vault_dev
```

## Usage:

```python
import vault_dev
vault_dev.ensure_installed()
# Did not find system vault, installing one for tests
# installing vault to '/tmp/tmpkzvlyw5c'
with vault_dev.server(verbose=True) as server:
  vault = server.client()
  vault.write("secret/key", value="password")
# Starting vault server on port 37355
# Waiting for server to become active
# .
# Connection made
# Configuring old-style kv engine at /secret
# Stopping vault server
```

## License

`vault-dev` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
