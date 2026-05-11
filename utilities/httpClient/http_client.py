import requests
import time

from .exceptions import HttpTimeout, HttpRequestFailed


class HttpClient:
    DEFAULT_TIMEOUT = 30

    def __init__(self, timeout=None):
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()

    def request(self, method, url, headers=None, params=None, json=None, data=None):
        start = time.time()

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                timeout=self.timeout
            )
        except requests.Timeout:
            raise HttpTimeout(f"Timeout while calling {url}")

        duration_ms = int((time.time() - start) * 1000)

        if not response.ok:
            raise HttpRequestFailed(response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            data = response.text

        return {
            "status_code": response.status_code,
            "data": data,
            "headers": dict(response.headers),
            "duration_ms": duration_ms
        }
