import logging
from typing import Any
from urllib.parse import urlparse

from .redaction import redact_headers, truncate_body

logger = logging.getLogger("studentpeeps.outbound")
provider_logger = logging.getLogger("studentpeeps.provider_api")
integration_logger = logging.getLogger("studentpeeps.integration")


def _host_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc or ""
    except Exception:
        return ""


def log_outbound_http(
    *,
    method: str,
    url: str,
    status_code: int | None,
    duration_ms: int,
    request_headers: dict | None = None,
    request_body: Any = None,
    response_body: Any = None,
    integration: str | None = None,
    error: str | None = None,
) -> None:
    level = logging.INFO
    if status_code is not None and status_code >= 500:
        level = logging.ERROR
    elif status_code is not None and status_code >= 400:
        level = logging.WARNING
    elif error:
        level = logging.ERROR

    host = _host_from_url(url)
    message = f"Outbound HTTP {method.upper()} {url}"
    if status_code is not None:
        message += f" → {status_code}"

    extra = {
        "event": "outbound_http",
        "http": {
            "method": method.upper(),
            "url": url,
            "status_code": status_code,
            "url_details": {"host": host},
        },
        "duration_ms": duration_ms,
        "request_headers": redact_headers(request_headers),
        "request_body": truncate_body(request_body),
        "response_body": truncate_body(response_body),
    }
    if integration:
        extra["integration"] = integration
    if error:
        extra["dd"] = {"error": {"message": error}}

    logger.log(level, message, extra=extra)


def log_provider_api_call(
    *,
    provider_id: str,
    method: str,
    url: str,
    request_headers: dict,
    request_body: Any,
    response_status: int,
    response_body: Any,
    signature: str,
    duration_ms: int | None,
) -> None:
    """Mirror ProviderApiLog rows to Datadog (DB logging remains unchanged)."""
    extra = {
        "event": "provider_api_call",
        "provider_id": provider_id,
        "integration": "woohoo",
        "http": {
            "method": method.upper(),
            "url": url,
            "status_code": response_status,
            "url_details": {"host": _host_from_url(url)},
        },
        "duration_ms": duration_ms,
        "request_headers": redact_headers(request_headers),
        "request_body": truncate_body(request_body),
        "response_body": truncate_body(response_body),
    }
    level = logging.INFO
    if response_status >= 500:
        level = logging.ERROR
    elif response_status >= 400:
        level = logging.WARNING

    provider_logger.log(
        level,
        f"Provider API {provider_id} {method.upper()} {url} → {response_status}",
        extra=extra,
    )


def log_integration_event(
    *,
    integration: str,
    action: str,
    success: bool,
    detail: dict | None = None,
    error: str | None = None,
) -> None:
    level = logging.INFO if success else logging.ERROR
    extra = {
        "event": "integration_call",
        "integration": integration,
        "dd": {"detail": detail or {}},
    }
    if error:
        extra["dd"]["error"] = {"message": error}

    integration_logger.log(
        level,
        f"{integration} {action} {'ok' if success else 'failed'}",
        extra=extra,
    )
