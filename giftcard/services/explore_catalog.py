from giftcard.models import ProviderProduct
from giftcard.services.gc_tile_style import product_tile_fields
from giftcard.services.purchase_availability import purchase_availability_for


def explore_product_card(product: ProviderProduct) -> dict:
    override = getattr(product, "override", None)
    display_name = (
        (override.name if override and override.name else None)
        or product.brand_name
        or product.name
    )
    margin = getattr(override, "margin", None) if override else None
    tile = product_tile_fields(product.sku, display_name, margin=margin)
    disc = tile["discount_pct"]
    if disc == int(disc):
        discount_label = f"{int(disc)}%"
    else:
        discount_label = f"{disc:g}%"

    avail = purchase_availability_for(product)
    category_name = (
        override.category.name
        if override and override.category_id
        else "Gift card"
    )

    return {
        "sku": product.sku,
        "name": display_name,
        "category_name": category_name,
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
