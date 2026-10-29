from django.core.management.base import BaseCommand

from main.models import PolicyPage
from main.services.policy_content import normalize_policy_html


class Command(BaseCommand):
    help = "Unescape and fix HTML stored on help-center policy pages."

    def handle(self, *args, **options):
        updated = 0
        for page in PolicyPage.objects.all():
            fixed = normalize_policy_html(page.content)
            if fixed != page.content:
                page.content = fixed
                page.save(update_fields=["content", "updated_at"])
                updated += 1
                self.stdout.write(f"Updated {page.slug}")
        self.stdout.write(self.style.SUCCESS(f"Done. {updated} page(s) updated."))
