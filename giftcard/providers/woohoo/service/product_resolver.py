from giftcard.models import ProviderProduct, ProductOverride

from giftcard.services.margin_pricing import margin_as_percent
from giftcard.services.product_copy import format_short_description_html
from giftcard.services.product_pricing import pricing_config_for_product


def format_margin(value):
    if value is None:
        return None

    pct = margin_as_percent(value)
    if pct == pct.to_integral_value():
        return f"{int(pct)}%"
    normalized = pct.normalize()
    return f"{normalized}%"

class ProductResolver:
    """
    Resolves product data using:
    1. ProductOverride (highest priority)
    2. ProviderProduct (fallback)
    """

    def __init__(self, sku: str):
        self.product = ProviderProduct.objects.select_related(
            "override"
        ).get(sku=sku)

        self.override = getattr(self.product, "override", None)

    def _value(self, field):
        """
        Return override value if exists and not null,
        else fallback to ProviderProduct.
        """
        if self.override:
            override_value = getattr(self.override, field, None)
            if override_value not in (None, "", []):
                return override_value

        return getattr(self.product, field, None)

    def _brand_logo_url(self):
        if self.override and self.override.brand_logo:
            return self.override.brand_logo.url
        provider_logo = getattr(self.product, "brand_logo", None)
        if provider_logo:
            return provider_logo
        return None

    def _tile_brand_logo_url(self):
        if self.override and self.override.brand_logo:
            return self.override.brand_logo.url
        return None

    def resolve(self) -> dict:
        """
        Returns final merged product data.
        """
        tnc_content = self._value("tnc_content")
        if not tnc_content:
            tnc_content = self.product.tnc_content or ""

        return {
            "sku": self.product.sku,
            "name": self._value("name"),
            "description": self._value("description"),
            "short_description": self.product.short_description or "",
            "short_description_html": format_short_description_html(
                self.product.short_description or ""
            ),
            "tnc_content": tnc_content,
            "tnc_link": self.product.tnc_link or "",
            "expiry_info": self.product.expiry_info or "",
            "brand_name": self._value("brand_name"),
            "brand_code": self._value("brand_code"),
            "brand_logo": self._brand_logo_url(),
            "tile_brand_logo": self._tile_brand_logo_url(),
            "thumbnail": self._value("thumbnail"),

            "min_price": self.product.min_price,
            "max_price": self.product.max_price,
            "currency": self.product.currency_code,
            **pricing_config_for_product(self.product),

            "category": (
                self.override.category
                if self.override and self.override.category
                else None
            ),

            "margin": (
                format_margin(self.override.margin)
                if self.override and self.override.margin is not None
                else None
            ),
            "margin_raw": (
                self.override.margin
                if self.override and self.override.margin is not None
                else 0
            ),
        }
