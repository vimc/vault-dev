import math
import os
import socket
import subprocess
import time
import uuid

import hvac
import requests

from vault_dev.utils import find_free_port


class server:
    def __init__(self, port=None, verbose=False, debug=False):
        self.port = port or find_free_port()
        self.addr = "http://localhost:{}".format(self.port)
        self.token = str(uuid.uuid4())
        self.debug = debug
        self.verbose = verbose or debug
        self.process = None

    def start(self, timeout=5, poll=0.1):
        if self.is_running():
            self._message("Vault server already started")
            return
        self._message("Starting vault server on port {}".format(self.port))
        args = ["vault", "server", "-dev",
                "-dev-listen-address", "localhost:{}".format(self.port),
                "-dev-root-token-id", self.token]
        output = None if self.debug else subprocess.PIPE
        self.process = subprocess.Popen(args, stderr=output, stdout=output)
        self._wait_until_active(timeout, poll)
        self._enable_kv1()

    def stop(self):
        self._message("Stopping vault server")
        self.process.kill()
        self.process.wait()

    def client(self):
        # See https://github.com/hvac/hvac/issues/421
        if "VAULT_ADDR" in os.environ:
            del os.environ["VAULT_ADDR"]
        if "VAULT_TOKEN" in os.environ:
            del os.environ["VAULT_TOKEN"]
        cl = hvac.Client(url=self.addr, token=self.token)
        assert cl.is_authenticated()
        return cl

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def is_running(self):
        return self.process and not self.process.poll()

    def _wait_until_active(self, timeout, poll):
        self._message("Waiting for server to become active")
        for i in range(math.ceil(timeout / poll)):
            if not self.is_running():
                self._process_output()
                raise Exception("Vault process has terminated")
            try:
                cl = self.client()
                if cl.sys.is_initialized():
                    self._message("\nConnection made")
                    return
            except:
                self._message(".", end="")
                time.sleep(poll)
        # self._process_output()
        raise Exception("Vault did not start in time")

    def _enable_kv1(self):
        self._message("Configuring old-style kv engine at /secret")
        cl = self.client()
        cl.sys.disable_secrets_engine(path="secret")
        cl.sys.enable_secrets_engine(backend_type="kv",
                                     path="secret",
                                     options={"version": 1})

    def _message(self, txt, **kwargs):
        if self.verbose:
            print(txt, **kwargs)

    def _process_output(self):
        out = self.process.stdout.read().decode("UTF-8") or "(none)"
        err = self.process.stderr.read().decode("UTF-8") or "(none)"
        print("\nstdout:\n{}\nstderr:\n{}\n".format(out, err))
