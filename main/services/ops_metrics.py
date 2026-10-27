"""Numbers shared by the admin dashboard, ops pages, and the daily staff digest."""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from accounts_v2.models import Register
from brands_v2.models import Offer, OfferDailyAnalytics
from giftcard.models import Order
from utilities.models import GiftCardSettings

LOW_CODE_THRESHOLD = 5
CHART_DAYS = 14

PAID_STATUSES = (
    Order.STATUS_PAYMENT_CONFIRMED,
    Order.STATUS_WOOHOO_PLACED,
    Order.STATUS_COMPLETED,
)

ATTENTION_STATUSES = (
    Order.STATUS_FAILED,
    Order.STATUS_PAYMENT_CONFIRMED,
    Order.STATUS_WOOHOO_PLACED,
)


def is_on_hold(order) -> bool:
    return isinstance(order.woohoo_response, dict) and bool(order.woohoo_response.get("on_hold"))


def offer_pulls_last_days(days=CHART_DAYS):
    """Static offer-code reveals per day, including days with no row."""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    rows = {
        row.date: row
        for row in OfferDailyAnalytics.objects.filter(date__gte=start, date__lte=today)
    }
    series = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        data = rows[day].offers_data if day in rows else {}
        if not isinstance(data, dict):
            data = {}
        total = 0
        for value in data.values():
            try:
                total += int(value or 0)
            except (TypeError, ValueError):
                continue
        series.append({
            "date": day,
            "total": total,
            "label": day.strftime("%d %b"),
        })
    peak = max((point["total"] for point in series), default=0) or 1
    for point in series:
        point["width"] = 0 if point["total"] == 0 else max(round(point["total"] / peak * 100, 1), 4)
    return series


def low_code_offers(threshold=LOW_CODE_THRESHOLD):
    offers = []
    queryset = (
        Offer.objects.filter(isStaticCode=False)
        .select_related("brand")
        .order_by("title")
    )
    for offer in queryset:
        codes = offer.codes if isinstance(offer.codes, list) else []
        remaining = len(codes)
        if remaining <= threshold:
            offers.append({
                "id": offer.pk,
                "custom_id": offer.custom_id,
                "title": offer.title,
                "brand": offer.brand.name if offer.brand_id else "",
                "remaining": remaining,
            })
    offers.sort(key=lambda row: (row["remaining"], row["title"].lower()))
    return offers


def attention_counts():
    failed = Order.objects.filter(status=Order.STATUS_FAILED).count()
    in_progress = Order.objects.filter(status=Order.STATUS_WOOHOO_PLACED).count()
    on_hold = 0
    confirmed_open = 0
    confirmed = Order.objects.filter(status=Order.STATUS_PAYMENT_CONFIRMED).only(
        "woohoo_response",
    )
    for order in confirmed.iterator():
        if is_on_hold(order):
            on_hold += 1
        else:
            confirmed_open += 1
    return {
        "failed": failed,
        "on_hold": on_hold,
        "in_progress": in_progress,
        "confirmed_open": confirmed_open,
        "total": failed + on_hold + in_progress + confirmed_open,
    }


def attention_rows(limit=200):
    orders = (
        Order.objects.filter(status__in=ATTENTION_STATUSES)
        .order_by("-created_at")[:limit]
    )
    rows = []
    for order in orders:
        held = is_on_hold(order)
        rows.append({
            "id": order.pk,
            "reference_id": order.reference_id,
            "status": order.status,
            "status_label": order.get_status_display(),
            "total_amount": order.total_amount,
            "customer_email": order.customer_email,
            "payment_gateway": order.payment_gateway,
            "gateway_order_id": order.gateway_order_id,
            "gateway_payment_id": order.gateway_payment_id,
            "woohoo_order_id": order.woohoo_order_id,
            "on_hold": held,
            "can_retry": (
                not held
                and order.status != Order.STATUS_FAILED
                and not order.is_vouchers_fetched
            ),
            "created_at": order.created_at,
        })
    return rows


def today_order_stats():
    today = timezone.localdate()
    queryset = Order.objects.filter(created_at__date=today)
    paid = queryset.filter(status__in=PAID_STATUSES)
    revenue = paid.aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    return {
        "count": queryset.count(),
        "paid_count": paid.count(),
        "revenue": revenue,
    }


def pulls_today(series):
    if not series:
        return 0
    return series[-1]["total"]


def build_alerts(attention, low_offers):
    alerts = []
    if attention["total"]:
        alerts.append({
            "text": (
                f"{attention['total']} gift card order{'s' if attention['total'] != 1 else ''} need a person "
                f"({attention['failed']} failed, {attention['on_hold']} on hold, "
                f"{attention['in_progress']} with Woohoo, {attention['confirmed_open']} paid but not placed)"
            ),
            "href_name": "admin:ops_orders",
        })
    if low_offers:
        alerts.append({
            "text": (
                f"{len(low_offers)} offer{'s' if len(low_offers) != 1 else ''} "
                f"ha{'ve' if len(low_offers) != 1 else 's'} {LOW_CODE_THRESHOLD} or fewer codes left"
            ),
            "href_name": "admin:ops_offers",
        })
    return alerts


def build_ops_summary():
    chart = offer_pulls_last_days()
    low_offers = low_code_offers()
    attention = attention_counts()
    orders_today = today_order_stats()
    today = timezone.localdate()
    signups_today = Register.objects.filter(created_at__date=today).count()
    alerts = build_alerts(attention, low_offers)
    return {
        "orders_today": orders_today,
        "signups_today": signups_today,
        "pulls_today": pulls_today(chart),
        "offer_chart": chart,
        "low_code_offers": low_offers,
        "attention": attention,
        "purchases_enabled": GiftCardSettings.purchases_are_enabled(),
        "alerts": alerts,
        "has_alerts": bool(alerts),
    }


def digest_recipients():
    emails = {
        email.strip()
        for email in User.objects.filter(is_active=True, is_staff=True)
        .exclude(email="")
        .values_list("email", flat=True)
        if email and email.strip()
    }
    extra = getattr(settings, "OPS_DIGEST_EMAILS", "") or ""
    for part in str(extra).split(","):
        if part.strip():
            emails.add(part.strip())
    return sorted(emails)


def digest_plain_text(summary) -> str:
    orders = summary["orders_today"]
    attention = summary["attention"]
    lines = [
        "Student Peeps daily ops digest",
        "",
        f"Gift card buying: {'ON' if summary['purchases_enabled'] else 'OFF'}",
        f"Orders created today: {orders['count']} ({orders['paid_count']} paid, Rs {orders['revenue']})",
        f"New signups today: {summary['signups_today']}",
        f"Static offer codes pulled today: {summary['pulls_today']}",
        "",
    ]
    if not summary["has_alerts"]:
        lines.append("Nothing is waiting on a person right now.")
        return "\n".join(lines)

    lines.append("Needs a person:")
    for alert in summary["alerts"]:
        lines.append(f"- {alert['text']}")

    if attention["total"]:
        lines.append("")
        lines.append("Latest orders:")
        for row in attention_rows(limit=15):
            hold = " on hold" if row["on_hold"] else ""
            lines.append(
                f"- {row['reference_id']} {row['status']}{hold} "
                f"Rs {row['total_amount']} gateway {row['payment_gateway']} "
                f"order {row['gateway_order_id'] or '-'} payment {row['gateway_payment_id'] or '-'}"
            )

    if summary["low_code_offers"]:
        lines.append("")
        lines.append("Low code pools:")
        for offer in summary["low_code_offers"][:20]:
            lines.append(
                f"- {offer['brand']}: {offer['title']} ({offer['remaining']} left, {offer['custom_id']})"
            )

    lines.append("")
    lines.append("Open /admin/ for the queues. Refunds stay in the payment gateway.")
    return "\n".join(lines)
