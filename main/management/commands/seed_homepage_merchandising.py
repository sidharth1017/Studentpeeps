from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import HomepageFeaturedSku, HomepageSection, PromoStripBanner
from main.services.homepage_merchandising import DEFAULT_PICKS_SPEC, DEFAULT_POPULAR_SKUS


class Command(BaseCommand):
    help = "Seed homepage sections, featured SKUs, and the Diwali promo strip (idempotent)."

    def handle(self, *args, **options):
        section_defaults = {
            "is_enabled": True,
            "starts_at": None,
            "ends_at": None,
        }
        fav_section, _ = HomepageSection.objects.update_or_create(
            section_key=HomepageSection.SECTION_STUDENT_FAVOURITES,
            defaults={
                **section_defaults,
                "title": "",
                "subtitle": "",
                "cta_label": "",
                "cta_href": "",
            },
        )
        pop_section, _ = HomepageSection.objects.update_or_create(
            section_key=HomepageSection.SECTION_POPULAR_WEEK,
            defaults=section_defaults,
        )

        if not fav_section.featured_skus.exists():
            for i, spec in enumerate(DEFAULT_PICKS_SPEC):
                HomepageFeaturedSku.objects.create(
                    section=fav_section,
                    sort_order=(i + 1) * 10,
                    sku=spec["sku"],
                    display_name=spec.get("name", ""),
                    subtitle=spec.get("why", ""),
                )
            self.stdout.write(self.style.SUCCESS(f"Added {len(DEFAULT_PICKS_SPEC)} student favourite SKUs."))

        if not pop_section.featured_skus.exists():
            for i, sku in enumerate(DEFAULT_POPULAR_SKUS):
                HomepageFeaturedSku.objects.create(
                    section=pop_section,
                    sort_order=(i + 1) * 10,
                    sku=sku,
                )
            self.stdout.write(self.style.SUCCESS(f"Added {len(DEFAULT_POPULAR_SKUS)} popular-week SKUs."))

        _, created = PromoStripBanner.objects.get_or_create(
            name="Diwali 2026",
            defaults={
                "is_enabled": True,
                "message": "Diwali is on Sunday, 8 November. Schedule gifts to land that morning.",
                "cta_label": "Diwali gifts",
                "cta_href": "/giftcard/explore/?category=entertainment",
                "background_color": "#14172F",
                "text_color": "#FFFFFF",
                "priority": 10,
                "starts_at": timezone.make_aware(datetime(2026, 9, 24, 0, 0)),
                "ends_at": timezone.make_aware(datetime(2026, 11, 8, 23, 59, 59)),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Diwali promo strip (24 Sep – 8 Nov 2026)."))

        self.stdout.write(self.style.SUCCESS("Done. Edit rows under Main in Django admin."))
