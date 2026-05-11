from giftcard.models import ProviderProduct, ProductOverride
from decimal import Decimal

def format_margin(value):
    if value is None:
        return None

    value = Decimal(value)

    # Percentage (0 < value < 1)
    if Decimal("0") < value < Decimal("1"):
        return f"{int(value * 100)}%"

    # Flat amount
    return f"₹{int(value)}"

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

    def resolve(self) -> dict:
        """
        Returns final merged product data.
        """
        return {
            "sku": self.product.sku,
            "name": self._value("name"),
            "description": self._value("description"),
            "tnc_content": self._value("tnc_content"),
            "brand_name": self._value("brand_name"),
            "brand_code": self._value("brand_code"),
            "brand_logo": self._value("brand_logo"),
            "thumbnail": self._value("thumbnail"),

            "min_price": self.product.min_price,
            "max_price": self.product.max_price,
            "currency": self.product.currency_code,
            "denominations": self.product.denominations,

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
