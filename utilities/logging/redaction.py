import copy
import re
from typing import Any

SENSITIVE_KEY_RE = re.compile(
    r"(password|secret|token|authorization|signature|api[_-]?key|clientsecret|"
    r"auth|credential|salt|merchant_key|access_key|private)",
    re.I,
)

REDACTED = "[REDACTED]"

# Woohoo / payment bodies often nest secrets under these keys.
SENSITIVE_EXACT_KEYS = frozenset(
    k.lower()
    for k in (
        "password",
        "clientSecret",
        "authorizationCode",
        "access_token",
        "token",
        "signature",
        "Authorization",
        "RAZORPAY_KEY_SECRET",
    )
)


def _redact_value(key: str, value: Any) -> Any:
    if key and (key.lower() in SENSITIVE_EXACT_KEYS or SENSITIVE_KEY_RE.search(key)):
        return REDACTED
    return value


def redact_mapping(data: dict | None) -> dict | None:
    if not data:
        return data
    out = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out[key] = redact_mapping(value)
        elif isinstance(value, list):
            out[key] = [
                redact_mapping(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            out[key] = _redact_value(str(key), value)
    return out


def redact_headers(headers: dict | None) -> dict | None:
    if not headers:
        return headers
    return {k: _redact_value(k, v) for k, v in headers.items()}


def truncate_body(body: Any, max_chars: int = 32_000) -> Any:
    if body is None:
        return None
    if isinstance(body, (dict, list)):
        body = copy.deepcopy(body)
        if isinstance(body, dict):
            return redact_mapping(body)
        return body
    text = body if isinstance(body, str) else str(body)
    if len(text) > max_chars:
        return text[:max_chars] + f"... [truncated {len(text) - max_chars} chars]"
    return text
