from django.core.management.base import BaseCommand
from giftcard.models import Provider
from giftcard.providers.woohoo.service.catalog_service import WoohooCatalogService


class Command(BaseCommand):
    help = "Sync Woohoo categories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category-ids",
            nargs="+",
            type=str,
            help="Specific Woohoo category IDs to sync"
        )

    def handle(self, *args, **options):
        provider = Provider.objects.filter(
            id="woohoo",
            is_active=True
        ).first()

        if not provider:
            self.stderr.write("Woohoo provider not found or inactive")
            return

        service = WoohooCatalogService(provider)

        category_ids = options.get("category_ids")

        if category_ids:
            self.stdout.write(f"Syncing categories: {category_ids}")
            service.sync_multiple_categories(category_ids)
        else:
            self.stderr.write(
                "No category IDs provided. "
                "Woohoo does not provide a list-all categories API."
            )

        self.stdout.write(self.style.SUCCESS("Woohoo category sync completed"))
