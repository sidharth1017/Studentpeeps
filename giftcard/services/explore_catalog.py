from giftcard.models import ProviderProduct
from giftcard.services.gc_tile_style import product_tile_fields
from giftcard.services.purchase_availability import purchase_availability_for


def tile_brand_name(product: ProviderProduct) -> str:
    override = getattr(product, "override", None)
    if override and (override.brand_name or "").strip():
        return override.brand_name.strip()
    if (product.brand_name or "").strip():
        return product.brand_name.strip()
    return ""


def tile_product_name(product: ProviderProduct) -> str:
    """Override display name, else provider catalog product name."""
    override = getattr(product, "override", None)
    if override and (override.name or "").strip():
        return override.name.strip()
    if (product.name or "").strip():
        return product.name.strip()
    return ""


def explore_product_card(product: ProviderProduct) -> dict:
    override = getattr(product, "override", None)
    brand_name = tile_brand_name(product)
    title = tile_product_name(product)
    margin = getattr(override, "margin", None) if override else None
    tile = product_tile_fields(product.sku, brand_name, margin=margin)
    disc = tile["discount_pct"]
    if disc == int(disc):
        discount_label = f"{int(disc)}%"
    else:
        discount_label = f"{disc:g}%"

    avail = purchase_availability_for(product)

    return {
        "sku": product.sku,
        "name": brand_name,
        "title": title,
        "category_name": brand_name,
        "brand_size_cls": tile["brand_size_cls"],
        "min_price": product.min_price,
        "max_price": product.max_price,
        "tile_brand_logo_url": product.tile_brand_logo_url,
        "pal_0": tile["pal_0"],
        "pal_1": tile["pal_1"],
        "pattern": tile["pattern"],
        "discount_label": discount_label,
        "can_purchase": avail.can_purchase,
        "availability_label": avail.short_label,
        "status_text": avail.status_text,
        "thumbnail_tag_text": avail.thumbnail_tag_text,
        "is_live": avail.is_live,
        "in_stock": avail.in_stock,
        "detail_url_name": "giftcard:giftcard_page",
    }
