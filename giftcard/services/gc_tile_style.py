"""Gift card art tokens (palette, pattern) for tiles — shared by search and home."""

BRAND_TILE = {
    "EGVGBPVRC001": {"discount": 12.0, "pal": ("#2442E6", "#6440E0"), "pt": "p-rings"},
    "EGCGBDEGCS001": {"discount": 4.5, "pal": ("#FF9F1C", "#F2542D"), "pt": "p-stars"},
    "EGCGBMYNC001": {"discount": 0.75, "pal": ("#7C3FD6", "#30177D"), "pt": "p-waves"},
    "EGVGBSTB001": {"discount": 3.75, "pal": ("#FF9F1C", "#F2542D"), "pt": "p-grid"},
    "EGCGBUBER001": {"discount": 1.5, "pal": ("#2FA8FF", "#2350DB"), "pt": "p-lines"},
    "EGCGBCROM001": {"discount": 0.5, "pal": ("#2442E6", "#6440E0"), "pt": "p-grid"},
    "EGCGBLVSS001": {"discount": 5.25, "pal": ("#C2337A", "#541750"), "pt": "p-stars"},
    "EGCGBSCLPL002": {"discount": 5.25, "pal": ("#7C3FD6", "#30177D"), "pt": "p-rings"},
    "EGCGBCINE001": {"discount": 16.5, "pal": ("#7C3FD6", "#30177D"), "pt": "p-grid"},
    "EGCGBWS002": {"discount": 5.25, "pal": ("#7C3FD6", "#30177D"), "pt": "p-waves"},
    "EGCGBAJIORRL001": {"discount": 3.25, "pal": ("#7C3FD6", "#30177D"), "pt": "p-waves"},
    "EGCGBGRDM001": {"discount": 0.75, "pal": ("#0A7368", "#17BF91"), "pt": "p-grid"},
    "EGCGBCCD001": {"discount": 6.75, "pal": ("#E3A866", "#B4602F"), "pt": "p-stars"},
    "EGCGBSUBW001": {"discount": 5.5, "pal": ("#FF9F1C", "#F2542D"), "pt": "p-rings"},
}

_DEFAULT = {"discount": 0, "pal": ("#2442E6", "#6440E0"), "pt": "p-dots"}


def _brand_size_cls(name: str) -> str:
    n = len(name or "")
    if n > 30:
        return "x3"
    if n > 22:
        return "xxl"
    if n > 14:
        return "xl"
    if n > 9:
        return "long"
    return ""


def _discount_from_margin(margin) -> float | None:
    if margin is None:
        return None
    m = float(margin)
    if 0 < m < 1:
        return m * 100
    return m


def product_tile_fields(sku: str, display_name: str, margin=None) -> dict:
    conf = BRAND_TILE.get(sku, _DEFAULT)
    disc = _discount_from_margin(margin)
    if disc is None:
        disc = float(conf.get("discount", 0))
    pal = conf.get("pal", _DEFAULT["pal"])
    return {
        "pal_0": pal[0],
        "pal_1": pal[1],
        "pattern": conf.get("pt", "p-dots"),
        "brand_size_cls": _brand_size_cls(display_name),
        "discount_pct": disc,
    }
