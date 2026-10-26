from decimal import Decimal

from django.test import SimpleTestCase

from giftcard.models import ProviderProduct
from giftcard.services.product_pricing import (
    amount_choices,
    allow_custom_amount,
    validate_denomination,
    _range_amount_choices,
    purchasable_denominations,
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

    def test_range_allows_multiples_of_10_in_band(self):
        p = self._product()
        self.assertTrue(validate_denomination(p, 1220)[0])
        self.assertFalse(validate_denomination(p, 1223)[0])
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

    def test_range_ui_presets_with_dynamic_top(self):
        self.assertEqual(
            _range_amount_choices(1, 10000),
            [250, 500, 1000, 1500, 2000, 5000],
        )
        self.assertEqual(
            _range_amount_choices(50, 5000),
            [250, 500, 1000, 1500, 2000, 5000],
        )
        self.assertEqual(
            _range_amount_choices(50, 3000),
            [250, 500, 1000, 1500, 2000, 3000],
        )
        self.assertEqual(_range_amount_choices(500, 10000), [500, 1000, 1500, 2000, 5000])

    def test_slab_shows_all_denoms_and_no_other(self):
        many = [
            100, 250, 300, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7500, 8000, 9500
        ]
        p = self._product(
            price_type="SLAB",
            min_price=Decimal("100"),
            max_price=Decimal("9500"),
            denominations=[str(x) for x in many],
        )
        self.assertEqual(amount_choices(p), many)
        self.assertFalse(allow_custom_amount(p))

    def test_slab_uses_woohoo_denominations_only(self):
        p = self._product(
            price_type="SLAB",
            min_price=Decimal("100"),
            max_price=Decimal("1000"),
            denominations=["100", "250", "500", "750", "1000"],
        )
        self.assertEqual(amount_choices(p), [100, 250, 500, 750, 1000])
        self.assertFalse(allow_custom_amount(p))

    def test_slab_excludes_denoms_above_max_price(self):
        p = self._product(
            price_type="SLAB",
            min_price=Decimal("50"),
            max_price=Decimal("5000"),
            denominations=["53", "105", "5250"],
        )
        self.assertEqual(purchasable_denominations(p), [53, 105])
        self.assertEqual(amount_choices(p), [53, 105])
        self.assertFalse(validate_denomination(p, 5250)[0])
