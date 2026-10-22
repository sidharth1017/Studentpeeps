import re
from dataclasses import dataclass

from giftcard.models import ProductOverride, ProviderProduct
from giftcard.providers.logo_dev.client import LogoDevClient, LogoDevError, LogoDevImage


@dataclass
class BrandLogoLookupResult:
    brand_name_used: str | None
    logo_domain_used: str | None
    image: LogoDevImage | None = None
    error: str | None = None


class BrandLogoLookup:
    GIFT_CARD_SUFFIX = re.compile(
        r"\s+(gift\s*card|egift\s*card|e-gift\s*card|voucher)\s*$",
        re.IGNORECASE,
    )

    def __init__(self, client: LogoDevClient | None = None):
        self.client = client or LogoDevClient()

    def resolve_merged_brand_name(
        self, product: ProviderProduct, override: ProductOverride | None
    ) -> str:
        if override and (override.brand_name or "").strip():
            return override.brand_name.strip()
        if (product.brand_name or "").strip():
            return product.brand_name.strip()
        name = (product.name or "").strip()
        if name:
            return self.GIFT_CARD_SUFFIX.sub("", name).strip() or name
        return ""

    def fetch_for_product(
        self,
        product: ProviderProduct,
        override: ProductOverride | None,
        *,
        skip_llm: bool = True,
    ) -> BrandLogoLookupResult:
        brand_name = self.resolve_merged_brand_name(product, override)
        domain = (override.logo_domain or "").strip() if override else ""

        try:
            if domain:
                image = self.client.fetch_logo(domain=domain)
                return BrandLogoLookupResult(
                    brand_name_used=brand_name or None,
                    logo_domain_used=domain,
                    image=image,
                )

            if brand_name:
                try:
                    image = self.client.fetch_logo(name=brand_name)
                    return BrandLogoLookupResult(
                        brand_name_used=brand_name,
                        logo_domain_used=None,
                        image=image,
                    )
                except LogoDevError:
                    search_domain = self.client.search_top_domain(brand_name)
                    if search_domain:
                        image = self.client.fetch_logo(domain=search_domain)
                        return BrandLogoLookupResult(
                            brand_name_used=brand_name,
                            logo_domain_used=search_domain,
                            image=image,
                        )
                    raise

            query = (product.name or "").strip()
            if query:
                search_domain = self.client.search_top_domain(query)
                if search_domain:
                    image = self.client.fetch_logo(domain=search_domain)
                    return BrandLogoLookupResult(
                        brand_name_used=brand_name or None,
                        logo_domain_used=search_domain,
                        image=image,
                    )

            if not skip_llm:
                pass

            return BrandLogoLookupResult(
                brand_name_used=brand_name or None,
                logo_domain_used=None,
                error="Could not resolve brand for Logo.dev lookup",
            )
        except LogoDevError as exc:
            return BrandLogoLookupResult(
                brand_name_used=brand_name or None,
                logo_domain_used=domain or None,
                error=str(exc),
            )
