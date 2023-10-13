import math
import subprocess
import time
import uuid

import hvac

from vault_dev.install import vault_path
from vault_dev.utils import drop_envvar, find_free_port, read_all_lines


class Server:
    def __init__(self, *, port=None, verbose=False, debug=False):
        self.process = None
        self.verbose = verbose or debug
        self.vault = vault_path()
        self.port = port or find_free_port()
        self.token = str(uuid.uuid4())
        self.debug = debug

    def start(self, timeout=5, poll=0.1):
        if self.is_running():
            self._message("Vault server already started")
            return
        self._message(f"Starting vault server on port {self.port}")
        args = [
            self.vault,
            "server",
            "-dev",
            "-dev-listen-address",
            f"localhost:{self.port}",
            "-dev-root-token-id",
            self.token,
        ]
        output = None if self.debug else subprocess.PIPE
        self.process = subprocess.Popen(args, stderr=output, stdout=output)
        self._wait_until_active(timeout, poll)
        self._enable_kv1()

    def stop(self, *, wait=True):
        self._message("Stopping vault server")
        if self.is_running():
            self.process.kill()
            if wait:
                self.process.wait()

    def client(self):
        # See https://github.com/hvac/hvac/issues/421
        drop_envvar("VAULT_ADDR")
        drop_envvar("VAULT_TOKEN")
        cl = hvac.Client(url=self.url(), token=self.token)
        assert cl.is_authenticated()  # noqa S101
        return cl

    def url(self):
        return f"http://localhost:{self.port}"

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, ex_type, ex_value, traceback):
        self.stop()

    def __del__(self):
        self.stop(wait=False)

    def is_running(self):
        return self.process and not self.process.poll()

    def _wait_until_active(self, timeout, poll):
        self._message("Waiting for server to become active")
        for _i in range(math.ceil(timeout / poll)):
            if not self.is_running():
                msg = "Vault process has terminated"
                raise VaultDevServerError(msg, self.process)
            try:
                cl = self.client()
                if cl.sys.is_initialized():
                    self._message("\nConnection made")
                    return
            except:  # noqa 82
                self._message(".", end="", flush=True)
                time.sleep(poll)
        msg = "Vault did not start in time"
        raise VaultDevServerError(msg, self.process)

    def _enable_kv1(self):
        self._message("Configuring old-style kv engine at /secret")
        cl = self.client()
        cl.sys.disable_secrets_engine(path="secret")
        cl.sys.enable_secrets_engine(
            backend_type="kv", path="secret", options={"version": 1}
        )

    def _message(self, txt, **kwargs):
        if self.verbose:
            print(txt, **kwargs)


class VaultDevServerError(Exception):
    def __init__(self, message, process):
        self.code = process.poll()
        if self.code:
            status = f"Process exited with code {self.code}"
        else:
            status = "Process is still running"
        if not self.code:
            print("Killing vault server process")
            process.kill()
            self.code = process.wait()
        self.stdout = read_all_lines(process.stdout, ">> ")
        self.stderr = read_all_lines(process.stderr, ">> ")
        out = self.stdout or "(none)"
        err = self.stderr or "(none)"
        self.msg = message
        self.message = f"{message}\n{status}\nstdout:\n{out}\nstderr:\n{err}"
