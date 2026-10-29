import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from giftcard.models import ProductOverride, ProviderProduct

DEFAULT_SHEET = Path(
    "/Users/sidharthverma/.cursor/projects/"
    "Users-sidharthverma-Studentpeeps-codebase-Studentpeeps/attachments/"
    "2f24a94b-689e-4363-9720-a724af1ef024/Discount_Sheet_-_Rates__1_.csv"
)


def _parse_margin(raw: str) -> Decimal | None:
    text = (raw or "").strip().replace("%", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _live_from_marker(raw: str) -> bool:
    value = (raw or "").strip().upper()
    if value in ("NOT LIVE", "NOT_LIVE", "NOTLIVE"):
        return False
    if value == "LIVE":
        return True
    return True


def _load_sheet(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


class Command(BaseCommand):
    help = (
        "Import rate sheet rows into ProductOverride (name, brand, margin, status). "
        "Woohoo sync updates ProviderProduct only; overrides are preserved."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default=str(DEFAULT_SHEET),
            help="Path to Discount_Sheet CSV",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without writing to the database",
        )

    def handle(self, *args, **options):
        path = Path(options["csv"])
        dry_run = options["dry_run"]

        if not path.is_file():
            self.stderr.write(self.style.ERROR(f"CSV not found: {path}"))
            raise SystemExit(1)

        rows = _load_sheet(path)
        db_skus = set(ProviderProduct.objects.values_list("sku", flat=True))

        missing_in_db = []
        updated = 0
        created = 0
        skipped_margin = 0

        @transaction.atomic
        def _apply():
            nonlocal updated, created, skipped_margin
            for row in rows:
                sku = (row.get("SKU ID") or row.get("SKU") or "").strip()
                if not sku:
                    continue
                if sku not in db_skus:
                    missing_in_db.append(sku)
                    continue

                product = ProviderProduct.objects.get(sku=sku)
                if dry_run:
                    try:
                        override = product.override
                    except ProductOverride.DoesNotExist:
                        override = ProductOverride(product=product)
                        created += 1
                else:
                    override, was_created = ProductOverride.objects.get_or_create(
                        product=product
                    )
                    if was_created:
                        created += 1

                name = (row.get("SKU name") or "").strip() or None
                brand_name = (row.get("Updated brand name") or "").strip() or None
                margin = _parse_margin(row.get("UPI discount %") or "")
                status = _live_from_marker(row.get("Live marker") or "")
                status_reason = (row.get("Status / reason") or "").strip() or None

                if margin is None and (row.get("UPI discount %") or "").strip():
                    skipped_margin += 1

                override.name = name
                override.brand_name = brand_name
                if margin is not None:
                    override.margin = margin
                override.status = status
                override.status_reason = status_reason

                if not dry_run:
                    update_fields = [
                        "name",
                        "brand_name",
                        "status",
                        "status_reason",
                        "updated_at",
                    ]
                    if margin is not None:
                        update_fields.insert(2, "margin")
                    override.save(update_fields=update_fields)
                updated += 1

        _apply()

        self.stdout.write(
            self.style.SUCCESS(
                f"{'[dry-run] ' if dry_run else ''}"
                f"Processed {updated} sheet rows "
                f"({created} new overrides)."
            )
        )
        if skipped_margin:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped invalid margin values for {skipped_margin} row(s)."
                )
            )
        if missing_in_db:
            self.stdout.write(
                self.style.WARNING(
                    f"{len(missing_in_db)} SKU(s) in sheet but not in catalog: "
                    f"{', '.join(sorted(missing_in_db)[:20])}"
                    f"{'…' if len(missing_in_db) > 20 else ''}"
                )
            )
