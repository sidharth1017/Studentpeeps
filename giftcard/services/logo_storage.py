import logging

import boto3
from botocore.config import Config
from django.conf import settings

logger = logging.getLogger(__name__)


def _object_key(relative_name: str) -> str:
    location = (getattr(settings, "AWS_LOCATION", "") or "").strip("/")
    name = relative_name.lstrip("/")
    if location:
        return f"{location}/{name}"
    return name


def make_media_object_public(relative_name: str) -> None:
    """Set public-read ACL on an object in the configured Spaces bucket."""
    if not relative_name:
        return

    bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
    if not bucket_name:
        logger.warning("make_media_object_public: AWS_STORAGE_BUCKET_NAME not set")
        return

    key = _object_key(relative_name)
    client = boto3.client(
        "s3",
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
        config=Config(signature_version="s3v4"),
    )
    try:
        client.put_object_acl(Bucket=bucket_name, Key=key, ACL="public-read")
    except Exception as exc:
        logger.exception("Failed public-read ACL on %s: %s", key, exc)
        raise
