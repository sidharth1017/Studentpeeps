import html
import re

# Word / Google Docs exports often hard-code black text, which breaks dark mode.
_DARK_TEXT_COLORS = frozenset(
    {
        "#000",
        "#000000",
        "black",
        "windowtext",
        "rgb(0, 0, 0)",
        "rgb(0,0,0)",
    }
)


def _is_dark_fixed_color(value: str) -> bool:
    v = (value or "").strip().lower().replace(" ", "")
    if v in _DARK_TEXT_COLORS:
        return True
    m = re.match(r"^rgb\((\d+),(\d+),(\d+)\)$", v)
    if m and m.group(1) == m.group(2) == m.group(3) == "0":
        return True
    return False


def _clean_style_attribute(style: str) -> str:
    parts = [p.strip() for p in style.split(";") if p.strip()]
    kept = []
    for part in parts:
        if ":" not in part:
            kept.append(part)
            continue
        prop, val = part.split(":", 1)
        prop_l = prop.strip().lower()
        val_l = val.strip().lower()
        if prop_l == "color":
            if _is_dark_fixed_color(val_l) or val_l == "transparent":
                continue
        if prop_l == "-webkit-text-fill-color" and _is_dark_fixed_color(val_l):
            continue
        kept.append(part)
    return "; ".join(kept)


def _strip_hardcoded_text_colors(text: str) -> str:
    def repl_double(match):
        cleaned = _clean_style_attribute(match.group(1))
        if not cleaned:
            return ""
        return f' style="{cleaned}"'

    def repl_single(match):
        cleaned = _clean_style_attribute(match.group(1))
        if not cleaned:
            return ""
        return f" style='{cleaned}'"

    text = re.sub(r'\sstyle="([^"]*)"', repl_double, text, flags=re.I)
    text = re.sub(r"\sstyle='([^']*)'", repl_single, text, flags=re.I)
    return text


def _fully_unescape(text: str) -> str:
    """Some imports are HTML-escaped once or twice inside a wrapper <p>."""
    prev = None
    while prev != text:
        prev = text
        if "&lt;" in text or "&gt;" in text or "&amp;" in text:
            text = html.unescape(text)
    return text


def normalize_policy_html(content: str) -> str:
    """
    Policy pages imported from Word/Summernote are sometimes stored HTML-escaped
    and wrapped in an outer <p>, which makes |safe render raw tags as text.
    Also strips fixed black text colors so light/dark theme tokens apply.
    """
    if not content or not content.strip():
        return content or ""

    text = _fully_unescape(content.strip())

    if text.startswith("<p>") and re.match(r"<p>\s*<(div|p)\b", text, re.I):
        inner = text[3:]
        if inner.rstrip().endswith("</p>"):
            inner = inner.rstrip()[:-4]
        text = inner.strip()

    text = _strip_hardcoded_text_colors(text)
    return text
