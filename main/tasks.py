import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

from main.services.ops_metrics import build_ops_summary, digest_plain_text, digest_recipients

logger = logging.getLogger(__name__)


def deliver_ops_digest():
    """Send the staff digest now. Returns who it was sent to."""
    summary = build_ops_summary()
    recipients = digest_recipients()
    if not recipients:
        logger.warning("Ops digest skipped: no staff emails and OPS_DIGEST_EMAILS is empty.")
        return {"sent": False, "recipients": [], "reason": "no recipients"}

    message = EmailMessage(
        "Student Peeps daily ops digest",
        digest_plain_text(summary),
        f"StudentPeeps <{settings.DEFAULT_FROM_EMAIL}>",
        recipients,
    )
    message.send(fail_silently=False)
    return {"sent": True, "recipients": recipients}


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def send_ops_digest():
    return deliver_ops_digest()
