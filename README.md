## vault-dev

[![Build Status](https://travis-ci.org/vimc/vault-dev.svg?branch=master)](https://travis-ci.org/vimc/vault-dev)
[![codecov.io](https://codecov.io/github/vimc/vault-dev/coverage.svg?branch=master)](https://codecov.io/github/vimc/vault-dev?branch=master)

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

## Publish to pypi

```shell
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

```
