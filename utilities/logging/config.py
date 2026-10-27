import logging

from .handlers import build_root_handlers


def configure_logging() -> None:
    """Apply Datadog-oriented logging (idempotent)."""
    if getattr(configure_logging, "_configured", False):
        return

    handlers = build_root_handlers()
    handler_refs = [h for h in handlers]

    logging.basicConfig(level=logging.INFO, handlers=handler_refs, force=True)

    for name in (
        "django",
        "django.request",
        "django.server",
        "celery",
        "giftcard",
        "accounts_v2",
        "studentpeeps",
        "studentpeeps.outbound",
        "studentpeeps.provider_api",
        "studentpeeps.integration",
        "studentpeeps.inbound",
    ):
        log = logging.getLogger(name)
        log.handlers = handler_refs
        log.propagate = False

    configure_logging._configured = True  # type: ignore[attr-defined]
