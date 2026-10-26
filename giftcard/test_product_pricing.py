from decimal import Decimal

from django.test import SimpleTestCase

from giftcard.models import ProviderProduct
from giftcard.services.product_pricing import (
    amount_choices,
    validate_denomination,
)
from giftcard.providers.woohoo.price_parser import parse_woohoo_product_price


class WoohooPriceParserTests(SimpleTestCase):
    def test_detail_range_domino_style(self):
        parsed = parse_woohoo_product_price(
            {
                "type": "RANGE",
                "min": "50",
                "max": "5000",
                "denominations": [],
            },
            list_min="50",
            list_max="5000",
        )
        self.assertEqual(parsed.price_type, "RANGE")
        self.assertEqual(parsed.min_price, Decimal("50"))
        self.assertEqual(parsed.max_price, Decimal("5000"))

    def test_detail_slab_uber_sandbox(self):
        parsed = parse_woohoo_product_price(
            {
                "type": "SLAB",
                "min": "500",
                "max": "1000",
                "denominations": ["500", "1000"],
            },
            list_min="1",
            list_max="10000",
        )
        self.assertEqual(parsed.price_type, "SLAB")
        self.assertEqual(parsed.min_price, Decimal("500"))


class DenominationValidationTests(SimpleTestCase):
    def _product(self, **kwargs):
        return ProviderProduct(
            min_price=kwargs.get("min_price", Decimal("50")),
            max_price=kwargs.get("max_price", Decimal("5000")),
            price_type=kwargs.get("price_type", "RANGE"),
            denominations=kwargs.get("denominations", []),
        )

    def test_range_allows_custom_in_band(self):
        p = self._product()
        self.assertTrue(validate_denomination(p, 1223)[0])
        self.assertFalse(validate_denomination(p, 6000)[0])

    def test_slab_requires_listed_amount(self):
        p = self._product(
            price_type="SLAB",
            min_price=Decimal("500"),
            max_price=Decimal("1000"),
            denominations=["500", "1000"],
        )
        self.assertTrue(validate_denomination(p, 500)[0])
        self.assertFalse(validate_denomination(p, 1223)[0])

    def test_amount_choices_slab(self):
        p = self._product(
            price_type="SLAB",
            min_price=Decimal("500"),
            max_price=Decimal("1000"),
            denominations=["500", "1000"],
        )
        self.assertEqual(amount_choices(p), [500, 1000])
