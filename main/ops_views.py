import logging

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View
from unfold.views import UnfoldSiteViewMixin

from giftcard.models import Order
from main.services.ops_metrics import (
    LOW_CODE_THRESHOLD,
    attention_counts,
    attention_rows,
    low_code_offers,
    offer_pulls_last_days,
)
from main.tasks import deliver_ops_digest

logger = logging.getLogger(__name__)


class OpsPage(UnfoldSiteViewMixin, View):
    permission_required = ()
    template_name = ""

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def _require_superuser(self, request):
        if request.user.is_superuser:
            return None
        return HttpResponseForbidden("Superuser access required.")


class OrdersAttentionView(OpsPage):
    title = "Orders needing attention"
    template_name = "admin/ops/orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = attention_rows()
        for row in rows:
            row["admin_url"] = reverse("admin:giftcard_order_change", args=[row["id"]])
        context.update({
            "rows": rows,
            "counts": attention_counts(),
            "subtitle": "Failed, on hold, or paid and not finished",
        })
        return context

    def post(self, request, *args, **kwargs):
        denied = self._require_superuser(request)
        if denied:
            return denied

        order = get_object_or_404(Order, pk=request.POST.get("order_id"))
        held = isinstance(order.woohoo_response, dict) and bool(order.woohoo_response.get("on_hold"))
        if held or order.status == Order.STATUS_FAILED or order.is_vouchers_fetched:
            messages.error(
                request,
                (
                    f"{order.reference_id} was not queued. "
                    "The Woohoo poll skips failed orders, on-hold orders, and orders that already have vouchers. "
                    "Refunds are done in the payment gateway."
                ),
            )
            return redirect(reverse("admin:ops_orders"))

        try:
            from giftcard.tasks import poll_woohoo_order_status_task
            poll_woohoo_order_status_task.delay(order.id)
        except Exception as exc:
            logger.exception("Could not queue Woohoo poll for %s", order.reference_id)
            messages.error(
                request,
                f"Could not queue the Woohoo poll for {order.reference_id}. Is Redis running? {exc}",
            )
        else:
            messages.success(
                request,
                f"Woohoo status poll queued for {order.reference_id}.",
            )
        return redirect(reverse("admin:ops_orders"))


class OfferHealthView(OpsPage):
    title = "Offer health"
    template_name = "admin/ops/offers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offers = low_code_offers()
        for offer in offers:
            offer["admin_url"] = reverse("admin:brands_v2_offer_change", args=[offer["id"]])
        context.update({
            "offers": offers,
            "threshold": LOW_CODE_THRESHOLD,
            "offer_chart": offer_pulls_last_days(),
            "shortcuts": [
                {"title": "Bulk upload offers", "href": reverse("bulk_upload")},
                {"title": "Homepage sections", "href": reverse("admin:main_homepagesection_changelist")},
                {"title": "Featured SKUs", "href": reverse("admin:main_homepagefeaturedsku_changelist")},
                {
                    "title": "Fetch brand logos",
                    "href": reverse("giftcard:admin_fetch_logos"),
                    "note": "Runs as soon as it opens.",
                },
            ],
            "subtitle": "Code pools and the last 14 days of reveals",
        })
        return context


class SendDigestView(OpsPage):
    title = "Send ops digest"
    template_name = "admin/ops/orders.html"

    def get(self, request, *args, **kwargs):
        return redirect(reverse("admin:index"))

    def post(self, request, *args, **kwargs):
        denied = self._require_superuser(request)
        if denied:
            return denied
        try:
            result = deliver_ops_digest()
        except Exception as exc:
            logger.exception("Ops digest failed")
            messages.error(request, f"Digest was not sent: {exc}")
        else:
            if result["sent"]:
                messages.success(
                    request,
                    "Digest sent to " + ", ".join(result["recipients"]),
                )
            else:
                messages.error(
                    request,
                    "No recipients. Add an email on a staff user, or set OPS_DIGEST_EMAILS.",
                )
        return redirect(reverse("admin:index"))
