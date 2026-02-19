from django.core.management.base import BaseCommand
from django.db import transaction

from giftcard.models import Provider
from giftcard.providers.woohoo.service.catalog_service import WoohooCatalogService


class Command(BaseCommand):
    help = "Sync Woohoo products category-wise"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category-id",
            type=str,
            help="Sync products for a specific provider category ID"
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

        service = WoohooCatalogService(provider)

        category_id = options.get("category_id")

        try:
            if category_id:
                self.stdout.write(
                    f"Syncing products for category {category_id}..."
                )
                service.sync_category_products_by_id(category_id)
            else:
                self.stdout.write(
                    "Syncing products for all Woohoo categories..."
                )
                service.sync_all_products()

            self.stdout.write(
                self.style.SUCCESS("Woohoo product sync completed successfully")
            )

        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Product sync failed: {exc}")
            )
            raise
