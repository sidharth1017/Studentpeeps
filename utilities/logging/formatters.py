import json
import logging
import traceback
from datetime import datetime, timezone

from django.conf import settings


class DatadogJsonFormatter(logging.Formatter):
    """JSON lines for Datadog Log Management (agent or HTTP intake)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "status": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": {"name": record.name},
            "ddsource": "python",
            "service": getattr(settings, "DD_SERVICE", "studentpeeps"),
            "env": getattr(settings, "DD_ENV", "development"),
        }
        version = getattr(settings, "DD_VERSION", "") or ""
        if version:
            payload["version"] = version

        for attr in (
            "event",
            "http",
            "integration",
            "provider_id",
            "duration_ms",
            "request_body",
            "response_body",
            "request_headers",
            "user_id",
            "dd",
        ):
            if hasattr(record, attr):
                payload[attr] = getattr(record, attr)

        if record.exc_info:
            payload["error"] = {
                "kind": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "stack": "".join(traceback.format_exception(*record.exc_info)),
            }

        return json.dumps(payload, default=str)
