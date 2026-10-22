from dataclasses import dataclass

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from giftcard.models import ProductOverride, Provider, ProviderProduct
from giftcard.providers.logo_dev.client import LogoDevError
from giftcard.services.brand_logo_lookup import BrandLogoLookup
from giftcard.services.brand_logo_reuse import (
    copy_brand_logo_to_product,
    find_sibling_logo_override,
)
from giftcard.services.logo_storage import make_media_object_public


@dataclass
class BrandLogoFetchResult:
    sku: str
    status: str
    brand_logo_url: str | None = None
    brand_name_used: str | None = None
    logo_domain_used: str | None = None
    error: str | None = None
    reason: str | None = None
    reused_from_sku: str | None = None


class BrandLogoFetchService:
    DEFAULT_PROVIDER_ID = "woohoo"

    def __init__(self, provider_id: str | None = None):
        self.provider = Provider.objects.filter(
            id=provider_id or self.DEFAULT_PROVIDER_ID,
            is_active=True,
        ).first()
        if not self.provider:
            raise ValueError("Gift card provider not found or inactive")
        self.lookup = BrandLogoLookup()

    def fetch_for_sku(
        self,
        sku: str,
        *,
        force: bool = False,
        skip_llm: bool = True,
    ) -> BrandLogoFetchResult:
        try:
            product = ProviderProduct.objects.select_related("override").get(
                provider=self.provider,
                sku=sku,
            )
        except ProviderProduct.DoesNotExist:
            return BrandLogoFetchResult(
                sku=sku,
                status="failed",
                error="Product not found for this provider",
            )

        return self._fetch_for_product(product, force=force, skip_llm=skip_llm)

    def fetch_all(
        self,
        *,
        force: bool = False,
        skip_llm: bool = True,
    ) -> list[BrandLogoFetchResult]:
        products = (
            ProviderProduct.objects.filter(provider=self.provider)
            .select_related("override")
            .order_by("sku")
        )
        return [
            self._fetch_for_product(product, force=force, skip_llm=skip_llm)
            for product in products
        ]

    def _fetch_for_product(
        self,
        product: ProviderProduct,
        *,
        force: bool,
        skip_llm: bool,
    ) -> BrandLogoFetchResult:
        sku = product.sku
        override = getattr(product, "override", None)

        if override and override.brand_logo and not force:
            return BrandLogoFetchResult(
                sku=sku,
                status="skipped",
                reason="override already has brand_logo",
                brand_logo_url=override.brand_logo.url,
                brand_name_used=self.lookup.resolve_merged_brand_name(product, override),
                logo_domain_used=(override.logo_domain or None),
            )

        brand_name_used = self.lookup.resolve_merged_brand_name(product, override)

        if not force:
            sibling = find_sibling_logo_override(product)
            if sibling and sibling.brand_logo:
                try:
                    with transaction.atomic():
                        override = copy_brand_logo_to_product(product, sibling)
                    return BrandLogoFetchResult(
                        sku=sku,
                        status="success",
                        brand_logo_url=override.brand_logo.url,
                        brand_name_used=brand_name_used,
                        logo_domain_used=override.logo_domain or None,
                        reason="reused existing brand logo",
                        reused_from_sku=sibling.product.sku,
                    )
                except Exception as exc:
                    return BrandLogoFetchResult(
                        sku=sku,
                        status="failed",
                        brand_name_used=brand_name_used,
                        error=f"Failed to copy brand logo: {exc}",
                    )

        try:
            lookup_result = self.lookup.fetch_for_product(
                product,
                override,
                skip_llm=skip_llm,
            )
        except LogoDevError as exc:
            return BrandLogoFetchResult(sku=sku, status="failed", error=str(exc))

        if lookup_result.error or not lookup_result.image:
            return BrandLogoFetchResult(
                sku=sku,
                status="failed",
                brand_name_used=lookup_result.brand_name_used,
                logo_domain_used=lookup_result.logo_domain_used,
                error=lookup_result.error or "Logo.dev returned no image",
            )

        image = lookup_result.image
        if (
            override
            and override.logo_dev_etag
            and override.logo_dev_etag == image.etag
            and override.brand_logo
            and not force
        ):
            return BrandLogoFetchResult(
                sku=sku,
                status="skipped",
                reason="logo etag unchanged",
                brand_logo_url=override.brand_logo.url,
                brand_name_used=lookup_result.brand_name_used,
                logo_domain_used=lookup_result.logo_domain_used,
            )

        try:
            with transaction.atomic():
                override, _ = ProductOverride.objects.get_or_create(product=product)
                filename = f"{sku}{image.file_ext}"
                override.brand_logo.save(
                    filename,
                    ContentFile(image.content),
                    save=False,
                )
                override.logo_dev_etag = image.etag
                override.logo_fetched_at = timezone.now()
                override.save(
                    update_fields=[
                        "brand_logo",
                        "logo_dev_etag",
                        "logo_fetched_at",
                    ]
                )
                make_media_object_public(override.brand_logo.name)
                stored_url = override.brand_logo.url
        except Exception as exc:
            return BrandLogoFetchResult(
                sku=sku,
                status="failed",
                brand_name_used=lookup_result.brand_name_used,
                logo_domain_used=lookup_result.logo_domain_used,
                error=f"Save to ProductOverride failed: {exc}",
            )

        return BrandLogoFetchResult(
            sku=sku,
            status="success",
            brand_logo_url=stored_url,
            brand_name_used=lookup_result.brand_name_used,
            logo_domain_used=lookup_result.logo_domain_used,
        )
