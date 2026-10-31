"""Flash message helpers for auth flows."""

from django.contrib import messages as msg_framework

# Substrings of messages that belong on gift-card/checkout pages, not login/OTP.
_CHECKOUT_FLASH_HINTS = (
    "gift card",
    "cart",
    "single order",
    "denomination",
    "not available to buy",
    "product not found",
)


def discard_all_flash_messages(request) -> None:
    """Consume every queued flash message (e.g. when opening login)."""
    for _ in msg_framework.get_messages(request):
        pass


def discard_checkout_flash_messages(request) -> None:
    """Drop stale cart/checkout flashes; keep auth/OTP messages."""
    kept = []
    for message in msg_framework.get_messages(request):
        text = str(message).lower()
        if any(hint in text for hint in _CHECKOUT_FLASH_HINTS):
            continue
        kept.append((message.level, str(message), message.extra_tags or ""))
    for level, text, extra in kept:
        msg_framework.add_message(request, level, text, extra_tags=extra)
