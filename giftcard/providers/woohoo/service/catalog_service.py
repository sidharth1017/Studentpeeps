from decimal import Decimal
from django.utils import timezone

from giftcard.models import (
    Provider,
    ProviderCategory,
    ProviderProduct,
)
from giftcard.providers.woohoo.api_client import WoohooApiClient
from giftcard.providers.woohoo import endpoints


class WoohooCatalogService:
    """
    Unified Woohoo Catalog Service

    Responsibilities:
    - Sync Provider Categories
    - Sync Provider Products (LIST API ONLY)

    Does NOT:
    - Call product detail API
    - Create category-product join tables
    """

    def __init__(self, provider: Provider):
        self.provider = provider
        self.client = WoohooApiClient(provider)

    # ==================================================
    # CATEGORY SYNC
    # ==================================================

    def sync_category_by_id(self, category_id: str):
        """
        Sync a single Woohoo category into ProviderCategory
        """
        endpoint = endpoints.CATEGORIES.format(id=category_id)

        data = self.client.request(
            method="GET",
            endpoint=endpoint
        )

        ProviderCategory.objects.update_or_create(
            provider=self.provider,
            provider_category_id=str(data.get("id")),
            defaults={
                "name": data.get("name", ""),
                "url": data.get("url", ""),
                "description": data.get("description"),
                "short_description": data.get("shortDescription"),
                "canonical_url": data.get("canonicalUrl"),
                "color_code": data.get("colorCode"),
                "bg_color_code": data.get("bgColorCode"),
                "offer_description": data.get("offerDescription"),
                "meta_index": (
                    bool(data.get("metaIndex"))
                    if data.get("metaIndex") is not None
                    else None
                ),
                "meta_keyword": data.get("metaKeyword"),
                "meta_title": data.get("pageTitle"),
                "meta_description": data.get("metaDescription"),
                "image": data.get("images", {}).get("image"),
                "thumbnail": data.get("images", {}).get("thumbnail"),
                "subcategory_filter": data.get("subCategoryFilter", False),
                "subcategories_count": data.get("subcategoriesCount", 0),
                "last_synced_at": timezone.now(),
            }
        )

    def sync_multiple_categories(self, category_ids: list[str]):
        """
        Sync multiple Woohoo categories
        """
        for category_id in category_ids:
            self.sync_category_by_id(category_id)

    # ==================================================
    # PRODUCT SYNC (LIST API ONLY)
    # ==================================================

    def sync_all_products(self):
        """
        Sync products for ALL existing ProviderCategory records
        """
        categories = ProviderCategory.objects.filter(
            provider=self.provider
        )

        for category in categories:
            self.sync_category_products(category)

    def sync_category_products_by_id(self, provider_category_id: str):
        """
        Sync products for a single ProviderCategory ID
        """
        category = ProviderCategory.objects.filter(
            provider=self.provider,
            provider_category_id=str(provider_category_id)
        ).first()

        if not category:
            raise ValueError(
                f"ProviderCategory {provider_category_id} not found"
            )

        self.sync_category_products(category)

    def sync_category_products(self, category: ProviderCategory):
        """
        Fetch and store products for a given category (LIST API)
        """
        endpoint = endpoints.CATEGORY_PRODUCTS.format(
            id=category.provider_category_id
        )

        data = self.client.request(
            method="GET",
            endpoint=endpoint
        )

        products = data.get("products", [])

        for item in products:
            self._upsert_product_from_list(item)

    # ==================================================
    # INTERNAL UPSERT (NULL SAFE)
    # ==================================================

    def _upsert_product_from_list(self, data: dict):
        """
        Insert / update ProviderProduct using category-product LIST API
        """
        sku = data.get("sku")
        if not sku:
            return  # skip invalid rows safely

        price_block = self._extract_price_block(data)

        ProviderProduct.objects.update_or_create(
            provider=self.provider,
            sku=sku,
            defaults={
                "name": data.get("name", ""),
                "url": data.get("url", ""),

                "min_price": self._to_decimal(data.get("minPrice")),
                "max_price": self._to_decimal(data.get("maxPrice")),

                "price_type": price_block.get("type"),
                "denominations": price_block.get("denominations", []),

                "thumbnail": data.get("images", {}).get("thumbnail", ""),
                "mobile_image": data.get("images", {}).get("mobile", ""),
                "base_image": data.get("images", {}).get("base", ""),
                "small_image": data.get("images", {}).get("small", ""),

                "brand_logo": data.get("brandLogo", ""),

                "currency_code": data.get("currency", {}).get("code", "INR"),
                "currency_symbol": data.get("currency", {}).get("symbol", "₹"),

                "provider_created_at": self._parse_datetime(
                    data.get("createdAt")
                ),
                "provider_updated_at": self._parse_datetime(
                    data.get("updatedAt")
                ),

                "last_list_synced_at": timezone.now(),
            }
        )

    # ==================================================
    # HELPERS (CRASH PROOF)
    # ==================================================

    def _extract_price_block(self, data: dict) -> dict:
        """
        Safely extract price block from Woohoo list API
        """
        price = data.get("price")

        if not isinstance(price, dict):
            return {}

        cpg = price.get("cpg")

        if isinstance(cpg, dict):
            for _, block in cpg.items():
                if isinstance(block, dict):
                    return block

        return {}

    def _to_decimal(self, value):
        try:
            return Decimal(value)
        except Exception:
            return Decimal("0")

    def _parse_datetime(self, value):
        try:
            return timezone.datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except Exception:
            return None
