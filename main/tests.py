from decimal import Decimal
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from brands_v2.models import Brand, Category, Offer, OfferDailyAnalytics
from giftcard.models import Order
from main.services.ops_metrics import build_ops_summary, low_code_offers
from main.tasks import deliver_ops_digest


TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02D\x01\x00;"
)


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class OpsDashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            "ops-staff", "ops-staff@example.com", "pass", is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            "ops-root", "ops-root@example.com", "pass",
        )
        self.today = timezone.localdate()
        OfferDailyAnalytics.objects.create(date=self.today, offers_data={"offer-a": 4, "offer-b": 1})
        Order.objects.create(
            reference_id="failed-1",
            total_amount=Decimal("100.00"),
            status=Order.STATUS_FAILED,
            customer_email="buyer@example.com",
            payment_gateway="payu",
            gateway_order_id="gw-order",
            gateway_payment_id="gw-pay",
        )
        Order.objects.create(
            reference_id="hold-1",
            total_amount=Decimal("80.00"),
            status=Order.STATUS_PAYMENT_CONFIRMED,
            customer_email="hold@example.com",
            payment_gateway="payu",
            woohoo_response={"on_hold": True},
        )
        self.polling = Order.objects.create(
            reference_id="woohoo-1",
            total_amount=Decimal("40.00"),
            status=Order.STATUS_WOOHOO_PLACED,
            customer_email="poll@example.com",
            payment_gateway="payu",
        )
        image = SimpleUploadedFile("logo.gif", TINY_GIF, content_type="image/gif")
        brand = Brand.objects.create(name="Test Brand", logo=image)
        category = Category.objects.create(category_id="snacks", name="Snacks")
        Offer.objects.create(
            brand=brand,
            title="Few codes",
            category=category,
            thumbnail_image=SimpleUploadedFile("thumb.gif", TINY_GIF, content_type="image/gif"),
            about="About",
            tnc="Terms",
            isStaticCode=False,
            codes=["only-one"],
        )

    def test_summary_counts_existing_rows(self):
        summary = build_ops_summary()
        self.assertEqual(summary["attention"]["failed"], 1)
        self.assertEqual(summary["attention"]["on_hold"], 1)
        self.assertEqual(summary["attention"]["in_progress"], 1)
        self.assertEqual(summary["pulls_today"], 5)
        self.assertEqual(len(summary["offer_chart"]), 14)
        self.assertTrue(summary["has_alerts"])
        self.assertEqual(low_code_offers()[0]["remaining"], 1)

    def test_staff_can_open_dashboard_and_queues(self):
        self.client.force_login(self.staff)
        index = self.client.get(reverse("admin:index"))
        self.assertEqual(index.status_code, 200)
        self.assertContains(index, "Orders today")
        self.assertContains(index, "Signups today")
        self.assertContains(index, "Needs attention")
        self.assertContains(index, "Orders needing attention")
        self.assertContains(index, "Offer health")
        self.assertContains(index, "Shortcuts")
        self.assertNotContains(index, "app-accounts_v2")
        self.assertNotContains(index, "app-giftcard")
        self.assertNotContains(index, "lg:h-0")
        self.assertContains(index, "--color-primary-600: oklch(18% 0 0)")
        self.assertNotContains(index, "302.321")
        orders = self.client.get(reverse("admin:ops_orders"))
        self.assertEqual(orders.status_code, 200)
        self.assertContains(orders, "failed-1")
        self.assertContains(orders, "gw-order")
        offers = self.client.get(reverse("admin:ops_offers"))
        self.assertEqual(offers.status_code, 200)
        self.assertContains(offers, "Few codes")

    def test_recent_actions_lists_this_users_admin_log(self):
        LogEntry.objects.create(
            user_id=self.staff.pk,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.staff.pk,
            object_repr="Ops staff profile",
            action_flag=ADDITION,
        )
        self.client.force_login(self.staff)
        index = self.client.get(reverse("admin:index"))
        self.assertContains(index, "Recent actions")
        self.assertContains(index, "Ops staff profile")

    def test_anonymous_dashboard_redirects_to_login(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    @patch("giftcard.tasks.poll_woohoo_order_status_task.delay")
    def test_retry_queues_woohoo_poll_and_skips_failed(self, delay):
        self.client.force_login(self.superuser)
        failed = Order.objects.get(reference_id="failed-1")
        skipped = self.client.post(reverse("admin:ops_orders"), {"order_id": failed.pk})
        self.assertEqual(skipped.status_code, 302)
        delay.assert_not_called()

        queued = self.client.post(reverse("admin:ops_orders"), {"order_id": self.polling.pk})
        self.assertEqual(queued.status_code, 302)
        delay.assert_called_once_with(self.polling.pk)

    def test_staff_cannot_retry(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:ops_orders"), {"order_id": self.polling.pk})
        self.assertEqual(response.status_code, 403)

    @patch("main.tasks.EmailMessage")
    def test_digest_goes_to_staff(self, email_cls):
        result = deliver_ops_digest()
        self.assertTrue(result["sent"])
        self.assertIn("ops-staff@example.com", result["recipients"])
        self.assertIn("ops-root@example.com", result["recipients"])
        email_cls.return_value.send.assert_called_once()
        body = email_cls.call_args.args[1]
        self.assertIn("failed-1", body)
        self.assertIn("Few codes", body)
