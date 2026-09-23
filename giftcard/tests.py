from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from giftcard.models import Order


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

    @patch('giftcard.views._place_woohoo_order')
    @patch('giftcard.views.get_gateway')
    def test_payu_success_callback_handles_woohoo_failure(self, mock_get_gateway, mock_place_woohoo_order):
        # Setup mocks
        mock_place_woohoo_order.return_value = False
        
        mock_verification = MagicMock()
        mock_verification.success = True
        
        mock_gw = MagicMock()
        mock_gw.verify_payment.return_value = mock_verification
        mock_get_gateway.return_value = mock_gw
        
        # Call PayU success callback
        payload = {"udf1": self.order.reference_id, "mihpayid": "payid_123"}
        response = self.client.post(reverse("giftcard:payu_success"), payload)
        
        # Verify redirect to order_failed_refund
        self.assertRedirects(response, reverse("giftcard:order_failed_refund", kwargs={"reference_id": self.order.reference_id}))
        
        # Verify order status is updated to FAILED
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_FAILED)

    @patch('giftcard.views._place_woohoo_order')
    @patch('giftcard.views.get_gateway')
    def test_razorpay_callback_handles_woohoo_failure(self, mock_get_gateway, mock_place_woohoo_order):
        # Setup mocks
        mock_place_woohoo_order.return_value = False
        
        mock_verification = MagicMock()
        mock_verification.success = True
        mock_verification.gateway_payment_id = "rzp_pay_123"
        
        mock_gw = MagicMock()
        mock_gw.verify_payment.return_value = mock_verification
        mock_get_gateway.return_value = mock_gw
        
        # Call Razorpay callback
        payload = {
            "order_id": self.order.id,
            "razorpay_order_id": "rzp_ord_123",
            "razorpay_payment_id": "rzp_pay_123",
            "razorpay_signature": "signature_123"
        }
        response = self.client.post(reverse("giftcard:payment_callback"), payload, content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["redirect"], reverse("giftcard:order_failed_refund", kwargs={"reference_id": self.order.reference_id}))
        
        # Verify order status is updated to FAILED
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_FAILED)

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

