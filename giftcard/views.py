from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import ProviderProduct, Cart, Order, PaymentTransaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
import json
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from types import SimpleNamespace
from giftcard.providers.woohoo.service.product_resolver import ProductResolver
from giftcard.services.cart_service import CartService
from giftcard.payments.registry import get_gateway
from giftcard.providers.woohoo.service.order_service import WoohooOrderService
from decimal import Decimal
from django.conf import settings
from uuid import uuid4


# ──────────────────────────────────────────────────────────────────────────────
# Cart Views
# ──────────────────────────────────────────────────────────────────────────────

class AddToCartView(View):
    def post(self, request):
        sku = request.POST.get("sku")
        denomination = request.POST.get("denomination")
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (ValueError, TypeError):
            quantity = 1
        buy_now = request.POST.get("buy_now") == "true"

        service = CartService(request)
        cart = service.get_cart()

        # Enforce total limit of 5
        current_qty = sum(int(item["quantity"]) for item in cart.items)
        if current_qty + quantity > 5:
            error_msg = "Oops! You can only place up to 5 gift cards in a single order."
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"error": error_msg}, status=400)
            else:
                from django.contrib import messages
                messages.error(request, error_msg)
                return redirect(request.META.get("HTTP_REFERER", "giftcard:explore"))

        resolver = ProductResolver(sku)
        product = resolver.resolve()
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        margin_raw = Decimal(str(product.get("margin_raw", 0)))
        unit_price = Decimal(str(denomination))

        if Decimal("0") < margin_raw < Decimal("1"):
            discount = unit_price * margin_raw
        else:
            discount = (unit_price * margin_raw) / Decimal("100")

        final_price = unit_price - discount

        product_data = {
            "sku": sku,
            "name": product["name"],
            "denomination": str(denomination),
            "quantity": quantity,
            "unit_price": str(unit_price),
            "margin": str(margin_raw),
            "final_price": str(final_price),
            "image": product.get("base_image") or product.get("thumbnail"),
        }

        service.add_item(product_data)

        if buy_now:
            return redirect("giftcard:cart_view")

        return JsonResponse({"message": "Added to cart", "cart_count": len(service.get_cart().items)})


class UpdateCartItemView(View):
    def post(self, request):
        sku = request.POST.get("sku")
        denomination = request.POST.get("denomination")
        try:
            quantity = int(request.POST.get("quantity"))
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid quantity"}, status=400)

        service = CartService(request)
        cart = service.get_cart()

        # Enforce total limit of 5
        other_items_qty = sum(
            int(item["quantity"]) for item in cart.items 
            if not (item["sku"] == sku and str(item["denomination"]) == str(denomination))
        )
        if other_items_qty + quantity > 5:
            return JsonResponse({"error": "Oops! You can only place up to 5 gift cards in a single order."}, status=400)

        service.update_item_quantity(sku, denomination, quantity)
        
        # Recalculate totals
        total_amount = float(cart.total_amount())
        
        return JsonResponse({
            "message": "Cart updated", 
            "cart_count": sum(int(item["quantity"]) for item in cart.items),
            "total_amount": total_amount
        })


class CartView(View):
    def get(self, request):
        service = CartService(request)
        cart = service.get_cart()
        
        user = request.user
        user_name = ""
        user_email = ""
        user_phone = ""
        if user.is_authenticated:
            from django.core.exceptions import ObjectDoesNotExist
            try:
                register = user.register
                user_phone = register.phone or ""
                first_name = register.firstname or user.first_name
                last_name = register.lastname or user.last_name
                user_name = f"{first_name} {last_name}".strip()
                user_email = register.institution_email or user.email
            except (ObjectDoesNotExist, AttributeError):
                user_name = f"{user.first_name} {user.last_name}".strip()
                user_email = user.email

        return render(request, "pages/cart_page.html", {
            "cart": cart,
            "total_amount": cart.total_amount(),
            "active_gateway": settings.ACTIVE_PAYMENT_GATEWAY,
            "user_name": user_name,
            "user_email": user_email,
            "user_phone": user_phone,
        })


class RemoveFromCartView(View):
    def post(self, request):
        sku = request.POST.get("sku")
        denomination = request.POST.get("denomination")
        service = CartService(request)
        service.remove_item(sku, denomination)
        return redirect("giftcard:cart_view")


# ──────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────────────────────────────────────

def _place_woohoo_order(order):
    """
    Calls the Woohoo API to place the gift card order.
    Safe — logs errors without raising so the payment success page still shows.
    Returns True if placed successfully.
    """
    customer = {
        "name":  order.customer_name,
        "email": order.customer_email,
        "phone": order.customer_phone,
    }
    import time
    import json
    
    for attempt in range(3):
        try:
            woohoo_service = WoohooOrderService()
            woohoo_response = woohoo_service.create_order(order, customer)

            # Check if Woohoo responded with an error dict directly
            if woohoo_response.get("code") and not str(woohoo_response.get("code")).startswith("2"):
                raise Exception(woohoo_response.get("message") or str(woohoo_response))

            woohoo_order_id = (
                woohoo_response.get("orderId")
                or woohoo_response.get("order_id")
                or woohoo_response.get("id", "")
            )
            order.status = Order.STATUS_WOOHOO_PLACED
            order.woohoo_order_id = str(woohoo_order_id)
            order.woohoo_response = woohoo_response
            order.save()
            
            return True
        except Exception as e:
            if attempt < 2:  # 0, 1
                time.sleep(1.5)  # wait 1.5s before retrying
                continue
                
            # If all 3 attempts fail, payment remains confirmed, Woohoo failed
            error_message = str(e)
            
            # Extract specific error message if it's an API exception
            if hasattr(e, 'response') and e.response:
                try:
                    err_dict = json.loads(e.response)
                    if "message" in err_dict:
                        error_message = err_dict["message"]
                except Exception:
                    pass

            order.woohoo_response = {"error": error_message, "attempts": attempt + 1}
            order.save(update_fields=["woohoo_response"])
            
            return False


# ──────────────────────────────────────────────────────────────────────────────
# Payment – Step 1: Initiate  (both Razorpay & PayU)
# ──────────────────────────────────────────────────────────────────────────────

class InitiatePaymentView(LoginRequiredMixin, View):
    """
    Creates an Order and a gateway payment order.

    - For modal gateways (Razorpay): returns JSON with gateway_order_id, key, amount.
    - For redirect gateways (PayU):  returns JSON with action_url + form_fields
      that the browser will auto-submit as a hidden HTML form.
    """
    login_url = "/account/v2/identify"

    def handle_no_permission(self):
        if self.request.headers.get("Content-Type") == "application/json" or self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"error": "Please login to continue.", "auth_required": True}, status=401)
        return super().handle_no_permission()

    def post(self, request):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, Exception):
            data = request.POST.dict()

        customer_name  = data.get("name", "").strip()
        customer_email = data.get("email", "").strip()
        customer_phone = data.get("phone", "").strip()

        if not all([customer_name, customer_email, customer_phone]):
            return JsonResponse({"error": "Name, email and phone are required."}, status=400)

        service = CartService(request)
        cart = service.get_cart()

        if not cart.items:
            return JsonResponse({"error": "Your cart is empty."}, status=400)

        total        = cart.total_amount()
        org_code     = getattr(settings, "WOOHOO_ORG_CODE", "STDPS")
        reference_id = f"{org_code}-{uuid4().hex}"
        gw_name      = settings.ACTIVE_PAYMENT_GATEWAY

        # 1. Create our Order
        order = Order.objects.create(
            user=request.user,
            reference_id=reference_id,
            total_amount=total,
            provider_id="woohoo",
            items_snapshot=cart.items,
            status=Order.STATUS_PAYMENT_INITIATED,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            payment_gateway=gw_name,
        )

        # 2. Build gateway-specific URLs (needed by redirect gateways)
        surl = request.build_absolute_uri(reverse("giftcard:payu_success"))
        furl = request.build_absolute_uri(reverse("giftcard:payu_failure"))

        # 3. Create gateway order
        gateway = get_gateway(gw_name)
        
        try:
            result = gateway.create_order(
                amount=total,
                currency="INR",
                reference_id=reference_id,
                customer={"name": customer_name, "email": customer_email, "phone": customer_phone},
                surl=surl,
                furl=furl,
            )
        except Exception as e:
            # Important: return JSON so the JS frontend `.json()` function doesn't crash on standard 500 HTML
            import logging
            logging.getLogger(__name__).error(f"Gateway creation error: {str(e)}")
            return JsonResponse({"error": f"Failed to initialize payment: {str(e)}"}, status=500)

        # 4. Store gateway_order_id & audit
        order.gateway_order_id = result.gateway_order_id
        order.save(update_fields=["gateway_order_id"])

        PaymentTransaction.objects.create(
            order=order,
            gateway=gw_name,
            gateway_order_id=result.gateway_order_id,
            amount=total,
            currency="INR",
            status="INITIATED",
        )

        # 5. Return gateway-type-aware response
        response_data = {
            "order_id":      order.id,
            "reference_id":  reference_id,
            "gateway_type":  result.gateway_type,
            "gateway_order_id": result.gateway_order_id,
            "amount":        result.amount_paise,
            "currency":      result.currency,
            "gateway_key":   result.gateway_key,
        }

        if result.gateway_type == "redirect":
            response_data["action_url"]   = result.action_url
            response_data["form_fields"]  = result.form_fields
        
        return JsonResponse(response_data)


# ──────────────────────────────────────────────────────────────────────────────
# Payment – Step 2a: Razorpay callback  (JS POST from browser)
# ──────────────────────────────────────────────────────────────────────────────

class PaymentCallbackView(LoginRequiredMixin, View):
    """
    Razorpay-specific: browser JS POSTs the payment result here after the modal closes.
    Verifies the signature, calls Woohoo API, clears cart.
    """
    login_url = "/account/v2/identify"

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, Exception):
            payload = request.POST.dict()

        our_order_id = payload.get("order_id")

        try:
            order = Order.objects.get(id=our_order_id, user=request.user)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found."}, status=404)

        if order.status != Order.STATUS_PAYMENT_INITIATED:
            return JsonResponse({"error": "Invalid order state."}, status=400)

        gateway = get_gateway(order.payment_gateway)
        verification = gateway.verify_payment(payload)

        # Audit log update
        PaymentTransaction.objects.filter(
            order=order,
            gateway_order_id=payload.get("razorpay_order_id", order.gateway_order_id)
        ).update(
            gateway_payment_id=verification.gateway_payment_id,
            status="SUCCESS" if verification.success else "FAILED",
            raw_response=payload,
        )

        if not verification.success:
            order.status = Order.STATUS_FAILED
            order.gateway_payment_id = verification.gateway_payment_id
            order.save()
            return JsonResponse({"error": verification.error_message, "redirect": "/giftcard/cart/"}, status=400)

        order.status = Order.STATUS_PAYMENT_CONFIRMED
        order.gateway_payment_id = verification.gateway_payment_id
        order.save()

        woohoo_success = _place_woohoo_order(order)
        CartService(request).clear_cart()

        if not woohoo_success:
            order.status = Order.STATUS_FAILED
            order.save(update_fields=["status"])
            return JsonResponse({
                "success": True,
                "redirect": reverse("giftcard:order_failed_refund", kwargs={"reference_id": order.reference_id}),
            })

        return JsonResponse({
            "success":  True,
            "redirect": reverse("giftcard:order_success", kwargs={"reference_id": order.reference_id}),
        })


# ──────────────────────────────────────────────────────────────────────────────
# Payment – Step 2b: PayU callbacks  (browser redirect from PayU)
# ──────────────────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class PayUSuccessView(View):
    """
    PayU POSTs to this URL after a successful payment.
    We verify the hash, then confirm the order and call Woohoo.
    CSRF exempt because PayU posts from their domain.
    """

    def post(self, request):
        payload = request.POST.dict()
        return self._handle(request, payload)

    def get(self, request):
        # Fallback for test redirects
        payload = request.GET.dict()
        return self._handle(request, payload)

    def _handle(self, request, payload):
        # reference_id is stored in udf1 by our PayU gateway
        reference_id = payload.get("udf1", "")

        try:
            order = Order.objects.get(reference_id=reference_id)
        except Order.DoesNotExist:
            return render(request, "pages/payment_failed.html", {
                "error": "Order not found. Please contact support."
            }, status=404)

        if order.status not in (Order.STATUS_PAYMENT_INITIATED,):
            # Already processed (duplicate callback) — redirect to correct page based on current status
            if order.status == Order.STATUS_FAILED:
                return redirect(reverse("giftcard:order_failed_refund", kwargs={"reference_id": order.reference_id}))
            return redirect(reverse("giftcard:order_success", kwargs={"reference_id": order.reference_id}))

        gateway = get_gateway(order.payment_gateway)
        verification = gateway.verify_payment(payload)

        mihpayid = payload.get("mihpayid", "")

        # Audit log
        PaymentTransaction.objects.filter(
            order=order,
            gateway_order_id=order.gateway_order_id,
        ).update(
            gateway_payment_id=mihpayid,
            status="SUCCESS" if verification.success else "FAILED",
            raw_response=payload,
        )

        if not verification.success:
            order.status = Order.STATUS_FAILED
            order.gateway_payment_id = mihpayid
            order.save()
            return render(request, "pages/payment_failed.html", {
                "error": verification.error_message,
                "order": order,
            })

        order.status = Order.STATUS_PAYMENT_CONFIRMED
        order.gateway_payment_id = mihpayid
        order.save()

        woohoo_success = _place_woohoo_order(order)

        # Clear cart manually instead of using CartService(request)
        # Because PayU POSTs back cross-domain without the SameSite session cookie,
        # interacting with request.session here triggers Django to generate a brand NEW session cookie,
        # which overwrites the user's logged-in session on the redirect, logging them out!
        if order.user:
            from giftcard.models import Cart
            cart = Cart.objects.filter(user=order.user, is_active=True).first()
            if cart:
                cart.items = []
                cart.save()

        if not woohoo_success:
            order.status = Order.STATUS_FAILED
            order.save(update_fields=["status"])
            return redirect(reverse("giftcard:order_failed_refund", kwargs={"reference_id": order.reference_id}))

        return redirect(reverse("giftcard:order_success", kwargs={"reference_id": order.reference_id}))


@method_decorator(csrf_exempt, name="dispatch")
class PayUFailureView(View):
    """PayU redirects here when payment fails or user cancels."""

    def post(self, request):
        payload = request.POST.dict()
        return self._handle(request, payload)

    def get(self, request):
        payload = request.GET.dict()
        return self._handle(request, payload)

    def _handle(self, request, payload):
        reference_id = payload.get("udf1", "")
        error_msg    = payload.get("error_Message") or payload.get("error_message") or "Payment was not completed."

        try:
            order = Order.objects.get(reference_id=reference_id)
            order.status = Order.STATUS_FAILED
            order.save(update_fields=["status"])

            PaymentTransaction.objects.filter(
                order=order,
                gateway_order_id=order.gateway_order_id
            ).update(status="FAILED", raw_response=payload)
        except Order.DoesNotExist:
            order = None

        return render(request, "pages/payment_failed.html", {
            "error": error_msg,
            "order": order,
        })


# ──────────────────────────────────────────────────────────────────────────────
# Order Success Page
# ──────────────────────────────────────────────────────────────────────────────

class OrderSuccessView(LoginRequiredMixin, View):
    login_url = "/account/v2/identify"

    def get(self, request, reference_id):
        order = get_object_or_404(Order, reference_id=reference_id, user=request.user)
        return render(request, "pages/order_success.html", {"order": order})


class OrderFailedRefundView(LoginRequiredMixin, View):
    login_url = "/account/v2/identify"

    def get(self, request, reference_id):
        order = get_object_or_404(Order, reference_id=reference_id, user=request.user)
        return render(request, "pages/order_failed_refund.html", {"order": order})


class OrderDetailView(LoginRequiredMixin, View):
    login_url = "/account/v2/identify"

    def get(self, request, reference_id):
        order = get_object_or_404(Order, reference_id=reference_id, user=request.user)
        
        is_terminal_status = order.status in (Order.STATUS_COMPLETED, Order.STATUS_FAILED)
        identifier = order.woohoo_order_id or order.reference_id

        # Only sync if not terminal OR if completed but missing vouchers
        if identifier and (not is_terminal_status or (order.status == Order.STATUS_COMPLETED and not order.is_vouchers_fetched)):
            from django.utils import timezone
            from datetime import timedelta
            
            # Check 30-second interval rate limit
            should_sync = True
            if order.updated_at and (timezone.now() - order.updated_at) < timedelta(seconds=30):
                # If updated less than 30s ago and vouchers are already fetched or order is in terminal state
                if is_terminal_status and order.is_vouchers_fetched:
                    should_sync = False
                elif not is_terminal_status and order.woohoo_response:
                    # Allow initial check or enforce 30s throttle
                    should_sync = False

            if should_sync:
                from giftcard.providers.woohoo.service.order_service import WoohooOrderService
                service = WoohooOrderService()

                # If completed but missing vouchers
                if order.status == Order.STATUS_COMPLETED and not order.is_vouchers_fetched:
                    try:
                        cards_response = service.get_activated_cards(identifier)
                        if cards_response and "cards" in cards_response:
                            order.woohoo_response = cards_response
                            order.is_vouchers_fetched = True
                            order.save()
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Error fetching vouchers for completed order: {str(e)}")

                elif not is_terminal_status:
                    try:
                        if order.woohoo_order_id:
                            response = service.get_order_status(order.woohoo_order_id)
                            # Fallback for timeout/indexing edge cases: if woohoo_order_id returns 5320, try status by refno
                            if response.get("code") == 5320:
                                response = service.get_order_status_by_refno(order.reference_id)
                        else:
                            # Timeout scenario where woohoo_order_id was never received
                            response = service.get_order_status_by_refno(order.reference_id)

                        woohoo_status = response.get("status", "").upper()
                        
                        # If woohoo returned valid orderId via refno lookup, save it
                        if response.get("orderId") or response.get("order_id"):
                            order.woohoo_order_id = str(response.get("orderId") or response.get("order_id"))

                        order.woohoo_response = response

                        if woohoo_status in ("COMPLETE", "COMPLETED"):
                            order.status = Order.STATUS_COMPLETED
                            try:
                                cards_target = order.woohoo_order_id or order.reference_id
                                cards_response = service.get_activated_cards(cards_target)
                                if cards_response and "cards" in cards_response:
                                    order.woohoo_response = cards_response
                                    order.is_vouchers_fetched = True
                            except Exception as card_err:
                                import logging
                                logging.getLogger(__name__).error(f"Error fetching activated cards: {str(card_err)}")

                            order.save()
                        elif woohoo_status in ("CANCELLED", "ERROR", "FAILED"):
                            order.status = Order.STATUS_FAILED
                            order.save()
                        elif woohoo_status == "PROCESSING":
                            if order.status != Order.STATUS_WOOHOO_PLACED:
                                order.status = Order.STATUS_WOOHOO_PLACED
                            order.save()
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Error syncing order status: {str(e)}")

        return render(request, "pages/order_detail.html", {"order": order})


# ──────────────────────────────────────────────────────────────────────────────
# Gift Card Product Page
# ──────────────────────────────────────────────────────────────────────────────

class GiftcardPageView(View):
    def get(self, request, sku):
        provider_product = get_object_or_404(ProviderProduct, sku=sku)

        resolver = ProductResolver(sku)
        giftcard_data = resolver.resolve()

        seo = SimpleNamespace()
        seo.title = giftcard_data.get("name") or "Student Peeps: Free Student Discounts"
        seo.description = giftcard_data.get("description") or "Get FREE Student Discounts on your favorite brands."
        seo.keywords = "student discounts, brand offers, gift cards"
        seo.og_url = request.build_absolute_uri()
        seo.canonical_url = request.build_absolute_uri(request.path)

        faqs = [
            {"question": "How to use this gift card?", "answer": f"Login to {giftcard_data.get('brand_name')} website, go to payment and enter the voucher code."},
            {"question": "What is the validity?", "answer": "Usually, these gift cards have a validity of 12 months from the date of issue."},
            {"question": "Is it refundable?", "answer": "Gift cards cannot be canceled or returned once issued."},
        ]

        similar_cards = [
            {"name": "Amazon Pay", "category": "Shopping", "offer": "2% off", "initial": "A", "color": "bg-yellow-500"},
            {"name": "Myntra", "category": "Fashion", "offer": "5% off", "initial": "M", "color": "bg-pink-500"},
            {"name": "BigBasket", "category": "Grocery", "offer": "3% off", "initial": "B", "color": "bg-green-500"},
        ]

        return render(request, "pages/giftcard_page.html", {
            "giftcard": giftcard_data,
            "provider_product": provider_product,
            "seo": seo,
            "faqs": faqs,
            "similar_cards": similar_cards,
        })

class ExploreView(View):
    def get(self, request):
        from brands_v2.models import Category
        from .models import ProductOverride, ProviderProduct
        
        query = request.GET.get('search', '')
        category_id = request.GET.get('category', 'all')
        sort_by = request.GET.get('sort', 'popular')
        selected_price_ranges = request.GET.getlist('price_range')
        
        # Category Icon & Color Mapping
        category_meta = {
            'fashion': {'icon': 'shirt', 'color': '#ff4d4d'},
            'tech': {'icon': 'smartphone', 'color': '#4d79ff'},
            'travel': {'icon': 'plane', 'color': '#4dff88'},
            'food_drink': {'icon': 'utensils-crossed', 'color': '#ffb347'},
            'health_beauty': {'icon': 'sparkles', 'color': '#ff66b2'},
            'home_utilities': {'icon': 'home', 'color': '#9966ff'},
            'education': {'icon': 'graduation-cap', 'color': '#4da6ff'},
            'entertainment': {'icon': 'play', 'color': '#ff4d4d'},
            'gaming': {'icon': 'gamepad-2', 'color': '#4d79ff'},
            'shopping': {'icon': 'shopping-bag', 'color': '#4dff88'},
            'grocery': {'icon': 'shopping-cart', 'color': '#ffb347'},
            'dining': {'icon': 'coffee', 'color': '#ff66b2'},
            'cabs': {'icon': 'car', 'color': '#9966ff'},
            'jewellery': {'icon': 'gem', 'color': '#4da6ff'},
            'fitness': {'icon': 'dumbbell', 'color': '#ff4d4d'},
        }
        
        # Base queryset
        products = ProviderProduct.objects.filter(in_stock=True).select_related('override', 'override__category')
        
        if query:
            products = products.filter(name__icontains=query)
            
        if category_id != 'all':
            products = products.filter(override__category__category_id=category_id)
            
        # Price range filter logic
        price_ranges = [
            {'id': 'under-250', 'label': 'Under ₹250', 'min': 0, 'max': 250},
            {'id': '250-500', 'label': '₹250 - ₹500', 'min': 250, 'max': 500},
            {'id': '500-1000', 'label': '₹500 - ₹1000', 'min': 500, 'max': 1000},
            {'id': '1000-2500', 'label': '₹1000 - ₹2500', 'min': 1000, 'max': 2500},
            {'id': '2500-above', 'label': '₹2500+', 'min': 2500, 'max': 999999},
        ]
        
        if selected_price_ranges:
            from django.db.models import Q
            range_queries = Q()
            for r_id in selected_price_ranges:
                for r in price_ranges:
                    if r['id'] == r_id:
                        range_queries |= Q(min_price__lte=r['max'], max_price__gte=r['min'])
            products = products.filter(range_queries)
            
        # Sorting
        if sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'price-low':
            products = products.order_by('min_price')
        elif sort_by == 'price-high':
            products = products.order_by('-min_price')
        else:
            products = products.order_by('-created_at')

        # Get categories with counts
        all_categories = Category.objects.filter(isVisible=True).order_by('sorting')
        
        # Total count
        total_count = ProviderProduct.objects.filter(in_stock=True).count()
        
        # Build URLs to preserve filters
        # 1. Category URLs
        categories_with_meta = []
        for cat in all_categories:
            meta = category_meta.get(cat.category_id, {'icon': 'sparkles', 'color': '#3b82f6'})
            count = ProviderProduct.objects.filter(in_stock=True, override__category=cat).count()
            
            cat_qd = request.GET.copy()
            cat_qd['category'] = cat.category_id
            
            categories_with_meta.append({
                'id': cat.category_id,
                'name': cat.name,
                'icon': meta['icon'],
                'color': meta['color'],
                'count': count,
                'url': '?' + cat_qd.urlencode()
            })
            
        # All Brands URL
        all_brands_qd = request.GET.copy()
        all_brands_qd['category'] = 'all'
        all_brands_url = '?' + all_brands_qd.urlencode()
            
        # 2. Sort URLs
        sort_urls = {}
        for s in ['popular', 'name', 'price-low', 'price-high']:
            sort_qd = request.GET.copy()
            sort_qd['sort'] = s
            key = s.replace('-', '_')
            sort_urls[key] = '?' + sort_qd.urlencode()
            
        # 3. Price range URLs & options
        price_ranges_meta = []
        for r in price_ranges:
            pr_qd = request.GET.copy()
            current_list = pr_qd.getlist('price_range')
            is_selected = r['id'] in current_list
            if is_selected:
                new_list = [x for x in current_list if x != r['id']]
            else:
                new_list = current_list + [r['id']]
            pr_qd.setlist('price_range', new_list)
            price_ranges_meta.append({
                'id': r['id'],
                'label': r['label'],
                'selected': is_selected,
                'url': '?' + pr_qd.urlencode()
            })
            
        # 4. Clear URL helpers
        # Clear category
        clear_cat_qd = request.GET.copy()
        clear_cat_qd.pop('category', None)
        clear_category_url = '?' + clear_cat_qd.urlencode()
        
        # Clear search
        clear_search_qd = request.GET.copy()
        clear_search_qd.pop('search', None)
        clear_search_url = '?' + clear_search_qd.urlencode()
        
        # Clear all
        clear_all_url = '?'
            
        context = {
            'products': products,
            'categories': categories_with_meta,
            'all_brands_url': all_brands_url,
            'total_count': total_count,
            'selected_category': category_id,
            'search_query': query,
            'sort_by': sort_by,
            'price_ranges': price_ranges_meta,
            'selected_price_ranges': selected_price_ranges,
            'sort_urls': sort_urls,
            'clear_category_url': clear_category_url,
            'clear_search_url': clear_search_url,
            'clear_all_url': clear_all_url,
        }
        return render(request, "pages/explore.html", context)