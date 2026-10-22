from pathlib import Path

from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone

from giftcard.models import ProductOverride, ProviderProduct
from giftcard.services.logo_storage import make_media_object_public


def find_sibling_logo_override(product: ProviderProduct) -> ProductOverride | None:
    """
    Another SKU's override with the same provider brand_name and an uploaded logo.
    """
    brand = (product.brand_name or "").strip()
    if not brand:
        return None

    return (
        ProductOverride.objects.exclude(product_id=product.pk)
        .filter(brand_logo__isnull=False)
        .exclude(brand_logo="")
        .filter(
            Q(product__brand_name__iexact=brand)
            | Q(brand_name__iexact=brand)
        )
        .select_related("product")
        .order_by("logo_fetched_at", "product__sku")
        .first()
    )


def copy_brand_logo_to_product(
    product: ProviderProduct,
    source: ProductOverride,
) -> ProductOverride:
    """Copy logo file + etag/domain metadata from source override to this SKU."""
    override, _ = ProductOverride.objects.get_or_create(product=product)

    suffix = Path(source.brand_logo.name).suffix or ".webp"
    with source.brand_logo.open("rb") as src:
        content = src.read()

    override.brand_logo.save(
        f"{product.sku}{suffix}",
        ContentFile(content),
        save=False,
    )
    override.logo_dev_etag = source.logo_dev_etag
    if source.logo_domain:
        override.logo_domain = source.logo_domain
    override.logo_fetched_at = timezone.now()
    override.save(
        update_fields=[
            "brand_logo",
            "logo_dev_etag",
            "logo_domain",
            "logo_fetched_at",
        ]
    )
    make_media_object_public(override.brand_logo.name)
    return override
