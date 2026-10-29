from __future__ import annotations

from dataclasses import dataclass

from giftcard.models import ProviderProduct

SOLD_OUT_LABEL = "Sold out"
OUT_OF_STOCK_LABEL = "Out of stock"


@dataclass(frozen=True)
class PurchaseAvailability:
    can_purchase: bool
    is_live: bool
    in_stock: bool
    short_label: str
    status_text: str
    thumbnail_tag_text: str
    detail_message: str
    sku: str


def _unavailable_copy(is_live: bool, in_stock: bool) -> tuple[str, str, str]:
    """
    Returns (status_text, thumbnail_tag_text, short_label) for storefront copy.
    Tag uses title case; CSS uppercases to SOLD OUT / OUT OF STOCK on the card.
    """
    if not in_stock and not is_live:
        return OUT_OF_STOCK_LABEL, OUT_OF_STOCK_LABEL, OUT_OF_STOCK_LABEL
    if not in_stock:
        return OUT_OF_STOCK_LABEL, OUT_OF_STOCK_LABEL, OUT_OF_STOCK_LABEL
    return SOLD_OUT_LABEL, SOLD_OUT_LABEL, SOLD_OUT_LABEL


def purchase_availability_for(product: ProviderProduct) -> PurchaseAvailability:
    override = getattr(product, "override", None)
    is_live = True if override is None else bool(override.status)
    in_stock = bool(product.in_stock)
    can_purchase = is_live and in_stock

    if can_purchase:
        return PurchaseAvailability(
            can_purchase=True,
            is_live=is_live,
            in_stock=in_stock,
            short_label="",
            status_text="",
            thumbnail_tag_text="",
            detail_message="",
            sku=product.sku,
        )

    status_text, thumbnail_tag_text, short_label = _unavailable_copy(is_live, in_stock)

    if not is_live and not in_stock:
        detail_message = (
            "This gift card is sold out and unavailable with the issuer right now."
        )
    elif not is_live:
        detail_message = (
            "This gift card is sold out on StudentPeeps. Browse available cards to buy today."
        )
    else:
        detail_message = (
            "This gift card is out of stock with the issuer. Check back later or pick another brand."
        )

    return PurchaseAvailability(
        can_purchase=False,
        is_live=is_live,
        in_stock=in_stock,
        short_label=short_label,
        status_text=status_text,
        thumbnail_tag_text=thumbnail_tag_text,
        detail_message=detail_message,
        sku=product.sku,
    )
