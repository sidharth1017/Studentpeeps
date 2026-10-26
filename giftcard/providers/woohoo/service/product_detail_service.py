from django.utils import timezone

from giftcard.models import ProviderProduct
from giftcard.providers.woohoo.api_client import WoohooApiClient
from giftcard.providers.woohoo import endpoints
from giftcard.providers.woohoo.price_parser import parse_woohoo_product_price


class WoohooProductDetailService:
    """
    Fetches and stores product detail data from Woohoo
    """

    def __init__(self, provider):
        self.provider = provider
        self.client = WoohooApiClient(provider)

    def fetch_and_update(self, product: ProviderProduct) -> ProviderProduct:
        """
        Fetch detail API using SKU and update ProviderProduct
        """
        endpoint = endpoints.PRODUCT_DETAIL.format(
            sku=product.sku
        )

        data = self.client.request(
            method="GET",
            endpoint=endpoint
        )

        price = data.get("price", {})
        parsed_price = parse_woohoo_product_price(
            price,
            list_min=data.get("minPrice"),
            list_max=data.get("maxPrice"),
        )

        product.provider_product_id = data.get("id")
        product.description = data.get("description")
        product.short_description = data.get("shortDescription")

        product.brand_name = data.get("brandName", "")
        product.brand_code = data.get("brandCode", "")
        product.brand_logo = data.get("brandLogo", product.brand_logo)

        currency = price.get("currency") if isinstance(price, dict) else {}
        if not isinstance(currency, dict):
            currency = {}
        product.currency_code = currency.get("code", product.currency_code)
        product.currency_symbol = currency.get("symbol", product.currency_symbol)

        product.min_price = parsed_price.min_price
        product.max_price = parsed_price.max_price
        product.price_type = parsed_price.price_type
        product.denominations = parsed_price.denominations

        product.expiry_info = data.get("expiry", "")
        product.tnc_content = data.get("tnc", {}).get("content", "")
        product.tnc_link = data.get("tnc", {}).get("link", "")

        product.in_stock = data.get("inStock", True)
        product.kyc_enabled = data.get("kycEnabled") == "1"
        product.disable_cart = data.get("disableCart", False)

        product.last_detail_synced_at = timezone.now()

        product.save(update_fields=[
            "provider_product_id",
            "description",
            "short_description",
            "brand_name",
            "brand_code",
            "brand_logo",
            "currency_code",
            "currency_symbol",
            "min_price",
            "max_price",
            "price_type",
            "denominations",
            "expiry_info",
            "tnc_content",
            "tnc_link",
            "in_stock",
            "kyc_enabled",
            "disable_cart",
            "last_detail_synced_at",
        ])

        return product
