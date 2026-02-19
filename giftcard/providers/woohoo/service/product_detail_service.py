from django.utils import timezone
from decimal import Decimal

from giftcard.models import ProviderProduct
from giftcard.providers.woohoo.api_client import WoohooApiClient
from giftcard.providers.woohoo import endpoints


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

        product.provider_product_id = data.get("id")
        product.description = data.get("description")
        product.short_description = data.get("shortDescription")

        product.brand_name = data.get("brandName", "")
        product.brand_code = data.get("brandCode", "")
        product.brand_logo = data.get("brandLogo", product.brand_logo)

        product.currency_code = price.get("currency", {}).get(
            "code", product.currency_code
        )
        product.currency_symbol = price.get("currency", {}).get(
            "symbol", product.currency_symbol
        )

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
            "expiry_info",
            "tnc_content",
            "tnc_link",
            "in_stock",
            "kyc_enabled",
            "disable_cart",
            "last_detail_synced_at",
        ])

        return product
