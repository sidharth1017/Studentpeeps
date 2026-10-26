from django.core.management.base import BaseCommand

from giftcard.models import Provider, ProviderApiLog, ProviderProduct
from giftcard.providers.woohoo.price_parser import parse_woohoo_product_price


class Command(BaseCommand):
    help = (
        "Backfill price_type, denominations, and min/max from cached Woohoo "
        "product detail API logs (no live API calls)."
    )

    def handle(self, *args, **options):
        provider = Provider.objects.filter(id="woohoo", is_active=True).first()
        if not provider:
            self.stderr.write(self.style.ERROR("Woohoo provider not found"))
            return

        latest_by_sku: dict[str, dict] = {}
        logs = ProviderApiLog.objects.filter(
            url__contains="/rest/v3/catalog/products/",
            response_status=200,
        ).order_by("id")

        for log in logs:
            if not log.response_body or not isinstance(log.response_body, dict):
                continue
            sku = log.url.rstrip("/").split("/")[-1]
            parsed = parse_woohoo_product_price(
                log.response_body.get("price"),
                list_min=log.response_body.get("minPrice"),
                list_max=log.response_body.get("maxPrice"),
            )
            if parsed.min_price <= 0 and parsed.max_price <= 0:
                continue
            latest_by_sku[sku] = log.response_body

        updated = 0
        missing = 0

        for product in ProviderProduct.objects.filter(provider=provider):
            data = latest_by_sku.get(product.sku)
            if not data:
                missing += 1
                continue

            parsed = parse_woohoo_product_price(
                data.get("price"),
                list_min=data.get("minPrice"),
                list_max=data.get("maxPrice"),
            )
            if parsed.min_price <= 0 and parsed.max_price <= 0:
                missing += 1
                continue

            product.min_price = parsed.min_price
            product.max_price = parsed.max_price
            product.price_type = parsed.price_type
            product.denominations = parsed.denominations
            product.save(
                update_fields=[
                    "min_price",
                    "max_price",
                    "price_type",
                    "denominations",
                ]
            )
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pricing backfill done: updated={updated}, no_log={missing}"
            )
        )
