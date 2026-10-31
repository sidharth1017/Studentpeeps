from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from giftcard.models import Cart, Order
from giftcard.provider_user_message import user_message_for_provider_error
from giftcard.services.cart_service import CartService
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore


class GuestCartMergeTests(TestCase):
    def test_merge_finds_cart_by_pre_login_session_key(self):
        user = User.objects.create_user(username="cartmerge", password="pass")
        guest_item = {
            "sku": "TEST-SKU",
            "name": "Test Card",
            "denomination": "500",
            "quantity": 1,
            "unit_price": "500",
            "margin": "0",
            "final_price": "500",
        }
        old_session_key = "guest-session-key-abc"
        Cart.objects.create(session_key=old_session_key, is_active=True, items=[guest_item])

        request = RequestFactory().get("/")
        request.session = SessionStore()
        request.session.create()
        request.user = AnonymousUser()
        request._guest_cart_session_key = old_session_key

        CartService(request).merge_guest_cart(user, guest_session_key=old_session_key)

        user_cart = Cart.objects.get(user=user, is_active=True)
        self.assertEqual(len(user_cart.items), 1)
        self.assertEqual(user_cart.items[0]["sku"], "TEST-SKU")
        self.assertFalse(Cart.objects.filter(session_key=old_session_key).exists())


class ProviderUserMessageTests(TestCase):
    def test_cloudfront_403_html_is_sanitized(self):
        raw = "HTTP 403: <!DOCTYPE HTML><TITLE>ERROR: The request could not be satisfied</TITLE>Request blocked."
        msg = user_message_for_provider_error(raw)
        self.assertNotIn("<!DOCTYPE", msg or "")
        self.assertNotIn("CloudFront", msg or "")
        self.assertIn("gift card partner", msg or "")

    def test_short_json_message_passthrough(self):
        raw = '{"message": "Insufficient wallet balance"}'
        self.assertEqual(user_message_for_provider_error(raw), "Insufficient wallet balance")


class OrderAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="orderaccess", password="password")
        self.client.force_login(self.user)

    def test_invalid_order_reference_shows_branded_not_found(self):
        response = self.client.get(
            reverse("giftcard:order_failed_refund", kwargs={"reference_id": "STDPS-not-a-real-order"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "pages/orders/not_found.html")
        self.assertNotContains(response, "URLconf")

    def test_other_users_order_is_not_found(self):
        other = User.objects.create_user(username="otheruser", password="password")
        Order.objects.create(
            user=other,
            reference_id="STDPS-secret-order",
            total_amount=100,
            provider_id="woohoo",
            status=Order.STATUS_COMPLETED,
        )
        response = self.client.get(
            reverse("giftcard:order_detail", kwargs={"reference_id": "STDPS-secret-order"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "pages/orders/not_found.html")


class GiftcardCallbackTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_login(self.user)
        
        # Create an initiated order
        self.order = Order.objects.create(
            user=self.user,
            reference_id="STDPS-testorder123",
            total_amount=100.00,
            provider_id="woohoo",
            status=Order.STATUS_PAYMENT_INITIATED,
            payment_gateway="payu"
        )

    @patch('giftcard.views._queue_woohoo_fulfillment')
    @patch('giftcard.views.get_gateway')
    def test_payu_success_callback_confirms_and_redirects_fast(self, mock_get_gateway, mock_queue):
        mock_verification = MagicMock()
        mock_verification.success = True
        mock_verification.gateway_payment_id = "payid_123"

        mock_gw = MagicMock()
        mock_gw.verify_payment.return_value = mock_verification
        mock_get_gateway.return_value = mock_gw

        payload = {"udf1": self.order.reference_id, "mihpayid": "payid_123"}
        response = self.client.post(reverse("giftcard:payu_success"), payload)

        self.assertRedirects(
            response,
            reverse("giftcard:order_success", kwargs={"reference_id": self.order.reference_id}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PAYMENT_CONFIRMED)
        mock_queue.assert_called_once()

    @patch('giftcard.views._queue_woohoo_fulfillment')
    @patch('giftcard.views.get_gateway')
    def test_payu_webhook_confirms_without_redirect(self, mock_get_gateway, mock_queue):
        mock_verification = MagicMock()
        mock_verification.success = True
        mock_verification.gateway_payment_id = "payid_webhook"

        mock_gw = MagicMock()
        mock_gw.verify_payment.return_value = mock_verification
        mock_get_gateway.return_value = mock_gw

        payload = {"udf1": self.order.reference_id, "mihpayid": "payid_webhook"}
        response = self.client.post(reverse("giftcard:payu_webhook"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "success")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PAYMENT_CONFIRMED)
        mock_queue.assert_called_once()

    @patch('giftcard.views._queue_woohoo_fulfillment')
    @patch('giftcard.views.get_gateway')
    def test_razorpay_callback_confirms_and_redirects_to_success(self, mock_get_gateway, mock_queue):
        mock_verification = MagicMock()
        mock_verification.success = True
        mock_verification.gateway_payment_id = "rzp_pay_123"

        mock_gw = MagicMock()
        mock_gw.verify_payment.return_value = mock_verification
        mock_get_gateway.return_value = mock_gw

        payload = {
            "order_id": self.order.id,
            "razorpay_order_id": "rzp_ord_123",
            "razorpay_payment_id": "rzp_pay_123",
            "razorpay_signature": "signature_123",
        }
        response = self.client.post(
            reverse("giftcard:payment_callback"), payload, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(
            data["redirect"],
            reverse("giftcard:order_success", kwargs={"reference_id": self.order.reference_id}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PAYMENT_CONFIRMED)
        mock_queue.assert_called_once()

    def test_payu_duplicate_callback_redirects_correctly(self):
        # If order status is FAILED, duplicate callback should redirect to order_failed_refund
        self.order.status = Order.STATUS_FAILED
        self.order.save()
        
        payload = {"udf1": self.order.reference_id}
        response = self.client.post(reverse("giftcard:payu_success"), payload)
        
        self.assertRedirects(response, reverse("giftcard:order_failed_refund", kwargs={"reference_id": self.order.reference_id}))


class PlaceWoohooOrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="password")
        self.order = Order.objects.create(
            user=self.user,
            reference_id="STDPS-refno123",
            total_amount=500.00,
            provider_id="woohoo",
            status=Order.STATUS_PAYMENT_CONFIRMED,
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="9999999999",
            payment_gateway="payu"
        )

    @patch('time.sleep', return_value=None)
    @patch('giftcard.views.WoohooOrderService')
    def test_place_woohoo_order_polls_refno_status_api(self, mock_service_cls, mock_sleep):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_service.create_order.return_value = {"orderId": "WH123", "status": "PROCESSING"}
        # Attempt 1: PROCESSING, Attempt 2: COMPLETE
        mock_service.get_order_status_by_refno.side_effect = [
            {"status": "PROCESSING", "orderId": "WH123"},
            {"status": "COMPLETE", "orderId": "WH123"}
        ]
        mock_service.get_activated_cards.return_value = {"cards": [{"cardNumber": "1234", "cardPin": "5678"}]}

        from giftcard.views import _place_woohoo_order
        result = _place_woohoo_order(self.order)

        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_COMPLETED)
        self.assertTrue(self.order.is_vouchers_fetched)
        # Verify get_order_status_by_refno was called with reference_id, NOT get_order_status
        mock_service.get_order_status_by_refno.assert_called_with(self.order.reference_id)
        mock_service.get_order_status.assert_not_called()
        self.assertEqual(mock_service.get_order_status_by_refno.call_count, 2)

    @patch('time.sleep', return_value=None)
    @patch('giftcard.views.WoohooOrderService')
    def test_place_woohoo_order_timeout_success_scenario(self, mock_service_cls, mock_sleep):
        """Simulates APITIMESUCC scenario: create_order times out, but refno status check resolves COMPLETE and triggers get_activated_cards."""
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        # create_order raises timeout exception
        mock_service.create_order.side_effect = Exception("HTTP Timeout on create_order")
        mock_service.get_order_status_by_refno.side_effect = [
            {"status": "PROCESSING", "orderId": "WHTIMEOUT123"},
            {"status": "COMPLETE", "orderId": "WHTIMEOUT123"}
        ]
        mock_service.get_activated_cards.return_value = {"cards": [{"cardNumber": "9999", "cardPin": "1111"}]}

        from giftcard.views import _place_woohoo_order
        result = _place_woohoo_order(self.order)

        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_COMPLETED)
        self.assertEqual(self.order.woohoo_order_id, "WHTIMEOUT123")
        self.assertTrue(self.order.is_vouchers_fetched)
        mock_service.get_activated_cards.assert_called_once_with("WHTIMEOUT123")

    @patch('time.sleep', return_value=None)
    @patch('giftcard.views.WoohooOrderService')
    def test_place_woohoo_order_timeout_failure_scenario(self, mock_service_cls, mock_sleep):
        """Simulates APITESTTIMFAIL scenario: create_order times out, and refno status check returns CANCELLED/FAILED."""
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_service.create_order.side_effect = Exception("HTTP Timeout on create_order")
        mock_service.get_order_status_by_refno.return_value = {"status": "CANCELLED", "orderId": "WHTIMEOUTFAIL"}

        from giftcard.views import _place_woohoo_order
        result = _place_woohoo_order(self.order)

        self.assertFalse(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_FAILED)
        mock_service.get_activated_cards.assert_not_called()

    @patch('time.sleep', return_value=None)
    @patch('giftcard.tasks.WoohooOrderService')
    def test_poll_woohoo_order_status_task_triggers_activated_cards(self, mock_service_cls, mock_sleep):
        """Tests that poll_woohoo_order_status_task automatically polls Woohoo status and calls get_activated_cards when COMPLETE."""
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_service.get_order_status_by_refno.side_effect = [
            {"status": "PROCESSING", "orderId": "WHBG123"},
            {"status": "COMPLETE", "orderId": "WHBG123"}
        ]
        mock_service.get_activated_cards.return_value = {"cards": [{"cardNumber": "8888", "cardPin": "2222"}]}

        from giftcard.tasks import poll_woohoo_order_status_task
        task_result = poll_woohoo_order_status_task(self.order.id, max_attempts=5, interval_seconds=0)

        self.assertTrue(task_result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_COMPLETED)
        self.assertTrue(self.order.is_vouchers_fetched)
        mock_service.get_activated_cards.assert_called_once_with("WHBG123")



