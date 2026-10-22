import logging
import time

logger = logging.getLogger("studentpeeps.inbound")


class RequestLoggingMiddleware:
    """Log every inbound HTTP request to Datadog (structured JSON)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start) * 1000)

        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.pk

        status = getattr(response, "status_code", None)
        level = logging.INFO
        if status and status >= 500:
            level = logging.ERROR
        elif status and status >= 400:
            level = logging.WARNING

        logger.log(
            level,
            f"Inbound {request.method} {request.path} → {status}",
            extra={
                "event": "inbound_http",
                "http": {
                    "method": request.method,
                    "url": request.build_absolute_uri(),
                    "status_code": status,
                    "url_details": {"path": request.path},
                },
                "duration_ms": duration_ms,
                "user_id": user_id,
            },
        )
        return response
