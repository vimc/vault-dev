## vault-dev

Use vault server in development mode in tests, from python

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
