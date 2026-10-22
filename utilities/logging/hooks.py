import time
from typing import Any

import requests

from .outbound import log_outbound_http

_installed = False


def install_requests_logging_hook() -> None:
    global _installed
    if _installed:
        return

    original = requests.Session.request

    def logged_request(self, method, url, **kwargs):  # noqa: ANN001
        url_str = str(url)
        if "http-intake.logs." in url_str or "datadoghq" in url_str:
            return original(self, method, url, **kwargs)

        start = time.time()
        response = None
        error = None
        try:
            response = original(self, method, url, **kwargs)
            return response
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            duration_ms = int((time.time() - start) * 1000)
            status = response.status_code if response is not None else None
            resp_body: Any = None
            if response is not None:
                try:
                    resp_body = response.json()
                except ValueError:
                    resp_body = response.text[:32_000] if response.text else ""

            req_body = kwargs.get("json") or kwargs.get("data") or kwargs.get("params")
            log_outbound_http(
                method=method,
                url=url,
                status_code=status,
                duration_ms=duration_ms,
                request_headers=kwargs.get("headers"),
                request_body=req_body,
                response_body=resp_body,
                error=error,
            )

    logged_request._sp_logged = True  # type: ignore[attr-defined]
    requests.Session.request = logged_request  # type: ignore[method-assign]
    _installed = True
