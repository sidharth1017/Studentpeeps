from django.core.management.base import BaseCommand
from django.db import transaction

from giftcard.models import Provider, ProviderProduct
from giftcard.providers.woohoo.service.product_detail_service import WoohooProductDetailService


class Command(BaseCommand):
    help = "Fetch and sync Woohoo product detail API for all products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sku",
            type=str,
            help="Sync detail for a single SKU (optional)"
        )

    def handle(self, *args, **options):
        provider = Provider.objects.filter(
            id="woohoo",
            is_active=True
        ).first()

        if not provider:
            self.stderr.write(
                self.style.ERROR("Woohoo provider not found or inactive")
            )
            return

        service = WoohooProductDetailService(provider)

        sku = options.get("sku")

        if sku:
            products = ProviderProduct.objects.filter(
                provider=provider,
                sku=sku
            )
        else:
            products = ProviderProduct.objects.filter(
                provider=provider
            )

        if not products.exists():
            self.stdout.write("No products found to sync")
            return

        self.stdout.write(
            f"Syncing Woohoo product details for {products.count()} product(s)..."
        )

        success = 0
        failed = 0

        for product in products.iterator(chunk_size=50):
            try:
                service.fetch_and_update(product)
                success += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    f"[FAILED] SKU {product.sku}: {exc}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Detail sync completed | Success: {success}, Failed: {failed}"
            )
        )
