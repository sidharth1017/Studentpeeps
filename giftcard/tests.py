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
