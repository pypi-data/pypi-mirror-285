import logging
import time

import requests

from rho_store.exceptions import RhoServerTimeout

logger = logging.getLogger(__name__)


class UptimeCheckHttpAdapter:
    default_timeout = 2.5

    def __init__(self, url: str, client_id: str = "python-sdk"):
        self.client_id = client_id
        self.url = url
        self.session = requests.Session()

    def check(self, timeout: float = None) -> bool:
        if timeout is None:
            timeout = self.default_timeout

        try:
            response = self.session.get(self.url, timeout=timeout, headers=self.get_headers())
            return response.status_code == 200
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout while checking {self.url}")
            return False

    def wait_until_ready(self, max_wait: float = 60.0) -> bool:
        start = time.time()
        while True:
            if self.check(timeout=1.0):
                return True
            if time.time() - start > max_wait:
                raise RhoServerTimeout(f"Timeout while waiting for {self.url} to be ready")
            print("Waiting for server to be ready...")
            time.sleep(2)

    def get_headers(self) -> dict:
        return {"X-Client-ID": self.client_id}


__all__ = ["UptimeCheckHttpAdapter"]
