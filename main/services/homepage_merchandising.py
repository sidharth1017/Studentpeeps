from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.utils import timezone

from giftcard.brand_design import BRAND_CONFIG, brand_size_class
from giftcard.models import ProviderProduct
from giftcard.services.catalog_visibility import sellable_giftcard_q
from giftcard.services.margin_pricing import margin_as_percent
from main.models import HomepageFeaturedSku, HomepageSection, PromoStripBanner


def _schedule_active(starts_at, ends_at, now=None) -> bool:
    now = now or timezone.now()
    if starts_at and now < starts_at:
        return False
    if ends_at and now > ends_at:
        return False
    return True


DEFAULT_PICKS_SPEC = [
    {"sku": "EGVGBPVRC001", "name": "PVR INOX", "why": "Movie nights"},
    {"sku": "EGCGBMYNC001", "name": "Myntra", "why": "Fashion"},
    {"sku": "EGCGBAJIORRL001", "name": "AJIO", "why": "Fashion"},
    {"sku": "EGCGBWS002", "name": "Westside", "why": "Fashion"},
    {"sku": "EGCGBSCLPL002", "name": "Lenskart", "why": "Glasses and lenses"},
    {"sku": "EGCGBGRDM001", "name": "Giva Silver", "why": "Silver jewellery"},
    {"sku": "EGCGBCINE001", "name": "Cinepolis", "why": "Movie nights"},
]

DEFAULT_POPULAR_SKUS = list(BRAND_CONFIG.keys())


@dataclass
class SectionPresentation:
    visible: bool
    title: str
    subtitle: str
    cta_label: str
    cta_href: str


def active_promo_strip():
    """Return promo strip context. Strip is hidden unless an enabled banner is in its schedule window."""
    now = timezone.now()
    campaigns = PromoStripBanner.objects.filter(is_enabled=True).order_by("-priority", "-id")
    active = [c for c in campaigns if _schedule_active(c.starts_at, c.ends_at, now)]
    banner = active[0] if active else None

    if not banner:
        return {"promo_strip_visible": False}

    link_color = banner.cta_color.strip() or banner.text_color
    return {
        "promo_strip_visible": True,
        "promo_strip_text": banner.message,
        "promo_strip_href": banner.cta_href,
        "promo_strip_link": banner.cta_label,
        "promo_strip_bg": banner.background_color,
        "promo_strip_color": banner.text_color,
        "promo_strip_link_color": link_color,
    }


def _section_presentation(section_key: str, defaults: dict) -> SectionPresentation:
    section = HomepageSection.objects.filter(section_key=section_key).first()
    if section is None:
        return SectionPresentation(
            visible=True,
            title=defaults["title"],
            subtitle=defaults["subtitle"],
            cta_label=defaults.get("cta_label", ""),
            cta_href=defaults.get("cta_href", ""),
        )
    if not section.is_enabled or not _schedule_active(section.starts_at, section.ends_at):
        return SectionPresentation(
            visible=False,
            title=defaults["title"],
            subtitle=defaults["subtitle"],
            cta_label=defaults.get("cta_label", ""),
            cta_href=defaults.get("cta_href", ""),
        )
    return SectionPresentation(
        visible=True,
        title=(section.title or defaults["title"]).strip(),
        subtitle=(section.subtitle or defaults["subtitle"]).strip(),
        cta_label=(section.cta_label or defaults.get("cta_label", "")).strip(),
        cta_href=(section.cta_href or defaults.get("cta_href", "")).strip(),
    )


def _active_featured_specs(section_key: str) -> list[dict]:
    now = timezone.now()
    rows = (
        HomepageFeaturedSku.objects.filter(section__section_key=section_key, is_enabled=True)
        .order_by("sort_order", "id")
    )
    specs = []
    for row in rows:
        if not _schedule_active(row.starts_at, row.ends_at, now):
            continue
        specs.append(
            {
                "sku": row.sku.strip(),
                "name": (row.display_name or "").strip(),
                "why": (row.subtitle or "").strip(),
            }
        )
    return specs


def _format_pick_inr(amount):
    rounded = round(float(amount) * 100) / 100
    if rounded == int(rounded):
        return f"₹{int(rounded):,}"
    return f"₹{rounded:,.2f}"


def _format_pick_disc(d):
    d = float(d)
    if d == int(d):
        return f"{int(d)}%"
    return f"{d:g}%"


def _pick_discount(prod, fallback):
    if prod:
        try:
            margin = prod.override.margin
            if margin is not None:
                return float(margin_as_percent(margin))
        except Exception:
            pass
    return float(fallback)


def _load_products(skus: Iterable[str]):
    sku_list = [s for s in skus if s]
    if not sku_list:
        return {}
    return {
        p.sku: p
        for p in ProviderProduct.objects.filter(
            sellable_giftcard_q(),
            sku__in=sku_list,
        ).select_related("override", "override__category")
    }


def build_hero_picks():
    defaults = {
        "title": "Student favourites",
        "subtitle": "Where students spend the most, priced for UPI.",
        "cta_label": "See all deals",
        "cta_href": "/giftcard/explore/?sort=disc",
    }
    presentation = _section_presentation(HomepageSection.SECTION_STUDENT_FAVOURITES, defaults)
    if not presentation.visible:
        return presentation, []

    db_specs = _active_featured_specs(HomepageSection.SECTION_STUDENT_FAVOURITES)
    picks_spec = db_specs if db_specs else DEFAULT_PICKS_SPEC

    products = _load_products(p["sku"] for p in picks_spec)
    sample_amt = 1000
    hero_picks = []

    for spec in picks_spec:
        sku = spec["sku"]
        conf = BRAND_CONFIG.get(sku, {})
        prod = products.get(sku)
        if not prod and not conf:
            continue
        pick_name = spec.get("name") or conf.get("display") or (prod.brand_name if prod else sku)
        why = spec.get("why") or ""
        if not why and prod and getattr(prod, "override", None) and prod.override.category:
            why = prod.override.category.name

        disc = _pick_discount(prod, conf.get("discount", 0))
        pay_val = sample_amt * (1 - disc / 100)
        hero_picks.append(
            {
                "sku": sku,
                "name": pick_name,
                "why": why,
                "discount": disc,
                "discount_display": _format_pick_disc(disc),
                "sample_amt_str": f"₹{sample_amt:,}",
                "pay_str": _format_pick_inr(pay_val),
                "brand_size_cls": brand_size_class(pick_name),
                "pal_0": conf.get("pal", ("#2442E6", "#6440E0"))[0],
                "pal_1": conf.get("pal", ("#2442E6", "#6440E0"))[1],
                "pattern_cls": conf.get("pt", "p-dots"),
            }
        )

    if not hero_picks:
        presentation.visible = False
    return presentation, hero_picks


def build_popular_cards():
    defaults = {
        "title": "Popular this week",
        "subtitle": "What people bought most in the last 7 days.",
        "cta_label": "See all",
        "cta_href": "/giftcard/explore/",
    }
    presentation = _section_presentation(HomepageSection.SECTION_POPULAR_WEEK, defaults)
    if not presentation.visible:
        return presentation, []

    db_specs = _active_featured_specs(HomepageSection.SECTION_POPULAR_WEEK)
    if db_specs:
        sku_order = [s["sku"] for s in db_specs]
    else:
        sku_order = DEFAULT_POPULAR_SKUS

    products = _load_products(sku_order)
    popular_cards = []

    for sku in sku_order:
        prod = products.get(sku)
        if not prod:
            continue
        conf = BRAND_CONFIG.get(sku, {})
        disp_brand = conf.get("display") or prod.brand_name or prod.name
        min_p = int(prod.min_price or 100)
        max_p = int(prod.max_price or 5000)
        if min_p == max_p:
            range_txt = f"₹{min_p:,}"
        else:
            range_txt = f"₹{min_p:,}–₹{max_p:,}"

        cat_name = "Gift card"
        if hasattr(prod, "override") and prod.override.category:
            cat_name = prod.override.category.name

        popular_cards.append(
            {
                "sku": prod.sku,
                "name": prod.name,
                "display_brand": disp_brand,
                "brand_size_cls": brand_size_class(disp_brand),
                "tile_brand_logo_url": prod.tile_brand_logo_url,
                "pal_0": conf.get("pal", ("#2442E6", "#6440E0"))[0],
                "pal_1": conf.get("pal", ("#2442E6", "#6440E0"))[1],
                "pattern_cls": conf.get("pt", "p-dots"),
                "discount_display": f"{conf.get('discount', 5.0)}%",
                "range_txt": range_txt,
                "category_name": cat_name,
                "use_txt": conf.get("use", "Online & in-store"),
                "use_icon": conf.get("use_icon", "i-store"),
                "min_price": min_p,
            }
        )

    if not popular_cards:
        presentation.visible = False
    return presentation, popular_cards


def max_brand_discount_pct():
    return max((c.get("discount", 0) for c in BRAND_CONFIG.values()), default=0)
