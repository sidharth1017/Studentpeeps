import html
import re


def normalize_policy_html(content: str) -> str:
    """
    Policy pages imported from Word/Summernote are sometimes stored HTML-escaped
    and wrapped in an outer <p>, which makes |safe render raw tags as text.
    """
    if not content or not content.strip():
        return content or ""

    text = content.strip()
    if "&lt;" in text:
        text = html.unescape(text)

    if text.startswith("<p>") and re.match(r"<p>\s*<(div|p)\b", text, re.I):
        inner = text[3:]
        if inner.rstrip().endswith("</p>"):
            inner = inner.rstrip()[:-4]
        text = inner.strip()

    return text
