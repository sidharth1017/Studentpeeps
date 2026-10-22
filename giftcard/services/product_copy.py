import re

from django.utils.safestring import mark_safe


def format_short_description_html(value: str):
    """Remove Woohoo-style leading bullets so list CSS can style items once."""
    if not value:
        return ""
    text = str(value)
    text = re.sub(r"(?i)&bull;\s*", "", text)
    text = re.sub(r"^\s*•\s*", "", text)
    text = re.sub(r"(<p[^>]*>)\s*•\s*", r"\1", text, flags=re.I)
    return mark_safe(text)
