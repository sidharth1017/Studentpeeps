class HttpClientError(Exception):
    pass


class HttpTimeout(HttpClientError):
    pass


class HttpRequestFailed(HttpClientError):
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        super().__init__(f"HTTP {status_code}: {response}")
