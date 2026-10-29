from django.core.management.base import BaseCommand

from brands_v2.services.offer_categories import assign_offer_categories


class Command(BaseCommand):
    help = "Assign browse categories to discount offers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without writing to the database.",
        )

    def handle(self, *args, **options):
        result = assign_offer_categories(dry_run=options["dry_run"])
        prefix = "Would update" if options["dry_run"] else "Updated"
        self.stdout.write(f"{prefix} {result['updated']} offer(s).")
        if result["unmapped_offers"]:
            self.stdout.write(
                self.style.WARNING(
                    "Unmapped custom_ids (left unchanged): "
                    + ", ".join(result["unmapped_offers"])
                )
            )
        if result["missing_category"]:
            self.stdout.write(
                self.style.ERROR(
                    "Missing Category rows: " + ", ".join(result["missing_category"])
                )
            )
