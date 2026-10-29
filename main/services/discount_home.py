"""Discount coupons homepage — same merchandising patterns as gift-card home."""

from __future__ import annotations

from giftcard.brand_design import brand_size_class

from brands_v2.models import Category, Offer
from main.views import brand_offer_count_map, offer_as_tile

CATEGORY_ICON_MAP = {
    "food-beverages": "i-cup",
    "food_drink": "i-cup",
    "fashion-lifestyle": "i-shirt",
    "fashion": "i-shirt",
    "entertainment": "i-ticket",
    "e-commerce": "i-bag",
    "shopping": "i-bag",
    "travel": "i-suitcase",
    "health-beauty": "i-heart",
    "electronics-appliances": "i-headphones",
    "tech": "i-headphones",
    "gaming": "i-gamepad",
    "grocery": "i-basket",
    "sportswear-footwear": "i-shoe",
    "sports": "i-shoe",
    "books": "i-book",
    "home-furnishings": "i-sofa",
    "home-needs": "i-home",
    "jewellery": "i-gem",
    "luxury-brands": "i-sparkle",
    "others": "i-tag",
}

OFFER_PALETTE_BY_CUSTOM_ID = {
    "spxspotify50": (("#1DB954", "#121212"), "p-waves"),
    "spxmyntra300": (("#FF3F6C", "#7C3FD6"), "p-waves"),
    "spxdell7percent": (("#007DB8", "#00447C"), "p-grid"),
    "spxmicrosoft365": (("#0078D4", "#005A9E"), "p-dots"),
    "spxindigo10": (("#0A2A66", "#E31E24"), "p-rings"),
    "spxrapido50": (("#FFE500", "#1A1A1A"), "p-lines"),
    "spxudemy100": (("#A435F0", "#5624D0"), "p-stars"),
    "spxapple10": (("#555555", "#1D1D1F"), "p-grid"),
    "spxprime50": (("#00A8E1", "#232F3E"), "p-dots"),
    "spxnotionfree": (("#2F2F2F", "#000000"), "p-lines"),
}

DEFAULT_PALETTE = (("#2442E6", "#6440E0"), "p-dots")

QUICK_CHIP_OFFER_IDS = [
    "spxspotify50",
    "spxmyntra300",
    "spxdell7percent",
    "spxmicrosoft365",
    "spxindigo10",
    "spxrapido50",
]

HERO_PICK_OFFER_IDS = [
    "spxdailyobjects15",
    "spxdell7percent",
    "spxnilkamal5",
    "spxblissclub10",
    "spxbb5",
    "spxwtf25",
]


def _palette_for_offer(offer: Offer):
    if offer.custom_id in OFFER_PALETTE_BY_CUSTOM_ID:
        return OFFER_PALETTE_BY_CUSTOM_ID[offer.custom_id]
    slug = (offer.brand.slug or "").split("-")[0]
    for key, val in OFFER_PALETTE_BY_CUSTOM_ID.items():
        if slug and slug in key:
            return val
    return DEFAULT_PALETTE


def enrich_offer_tile(offer: Offer, brand_offer_map: dict) -> dict:
    tile = offer_as_tile(offer, brand_offer_map)
    cat = offer.category
    tile["category_name"] = cat.name if cat else "Coupon"
    tile["category_id"] = cat.category_id if cat else ""
    (pal_0, pal_1), pattern_cls = _palette_for_offer(offer)
    tile["pal_0"] = pal_0
    tile["pal_1"] = pal_1
    tile["pattern_cls"] = pattern_cls
    tile["brand_size_cls"] = brand_size_class(offer.brand.name)
    tile["why"] = (offer.subtitle or tile["category_name"]).strip()
    tile["badge"] = "Exclusive" if offer.isExclusive else "Open offer"
    return tile


def discount_categories_for_home():
    rows = (
        Category.objects.filter(isVisible=True, offers__isnull=False)
        .distinct()
        .order_by("sorting")
    )
    out = []
    for cat in rows:
        slug = cat.category_id or ""
        icon = CATEGORY_ICON_MAP.get(
            slug,
            CATEGORY_ICON_MAP.get(slug.lower().replace(" ", "-"), "i-tag"),
        )
        out.append(
            {
                "name": cat.name,
                "category_id": slug,
                "icon": icon,
                "count": Offer.objects.filter(category=cat).count(),
            }
        )
    return out


def _ordered_tiles(offer_ids: list[str], brand_offer_map: dict) -> list[dict]:
    qs = Offer.objects.filter(custom_id__in=offer_ids).select_related("brand", "category")
    by_id = {o.custom_id: o for o in qs}
    tiles = []
    for oid in offer_ids:
        offer = by_id.get(oid)
        if offer:
            tiles.append(enrich_offer_tile(offer, brand_offer_map))
    return tiles


def build_discount_home_context(*, featured_sample: list[Offer] | None = None):
    brand_offer_map = brand_offer_count_map()
    hero_picks = _ordered_tiles(HERO_PICK_OFFER_IDS, brand_offer_map)
    quick_chips = _ordered_tiles(QUICK_CHIP_OFFER_IDS, brand_offer_map)

    if featured_sample is None:
        featured_sample = list(Offer.objects.select_related("brand", "category").order_by("-sorting")[:12])

    popular_rail = [enrich_offer_tile(o, brand_offer_map) for o in featured_sample[:10]]
    trending_rail = hero_picks[:6] if hero_picks else popular_rail[:6]

    return {
        "discount_categories": discount_categories_for_home(),
        "hero_picks": hero_picks,
        "quick_chips": quick_chips,
        "popular_rail": popular_rail,
        "trending_rail": trending_rail,
    }
