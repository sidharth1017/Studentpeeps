from django.urls import reverse

from main.services.ops_metrics import LOW_CODE_THRESHOLD, build_ops_summary


def dashboard_callback(request, context):
    summary = build_ops_summary()
    orders = summary["orders_today"]
    attention = summary["attention"]
    purchases = "ON" if summary["purchases_enabled"] else "OFF"

    def link(name):
        return reverse(name)

    kpi_cards = [
        {
            "title": "Orders today",
            "value": orders["count"],
            "detail": f"{orders['paid_count']} paid · Rs {orders['revenue']}",
            "href": link("admin:ops_orders"),
        },
        {
            "title": "Need a person",
            "value": attention["total"],
            "detail": (
                f"{attention['failed']} failed · {attention['on_hold']} on hold · "
                f"{attention['in_progress']} with Woohoo"
            ),
            "href": link("admin:ops_orders"),
        },
        {
            "title": "Signups today",
            "value": summary["signups_today"],
            "detail": "Email and phone signups",
            "href": link("admin:accounts_v2_register_changelist"),
        },
        {
            "title": "Codes pulled today",
            "value": summary["pulls_today"],
            "detail": "Static offer reveals",
            "href": link("admin:ops_offers"),
        },
        {
            "title": "Gift card buying",
            "value": purchases,
            "detail": "Utilities · gift card settings",
            "href": link("admin:utilities_giftcardsettings_changelist"),
        },
        {
            "title": "Low code pools",
            "value": len(summary["low_code_offers"]),
            "detail": f"{LOW_CODE_THRESHOLD} or fewer codes left",
            "href": link("admin:ops_offers"),
        },
    ]

    alerts = []
    for alert in summary["alerts"]:
        alerts.append({
            "text": alert["text"],
            "href": reverse(alert["href_name"]),
        })

    shortcuts = [
        {"title": "Bulk upload offers", "href": reverse("bulk_upload")},
        {"title": "Homepage sections", "href": reverse("admin:main_homepagesection_changelist")},
        {"title": "Featured SKUs", "href": reverse("admin:main_homepagefeaturedsku_changelist")},
        {"title": "Promo strip", "href": reverse("admin:main_promostripbanner_changelist")},
        {
            "title": "Fetch brand logos",
            "href": reverse("giftcard:admin_fetch_logos"),
            "note": "Opens the logo job. It runs as soon as the page loads.",
        },
    ]

    context.update({
        "title": "Dashboard",
        "kpi_cards": kpi_cards,
        "alerts": alerts,
        "offer_chart": summary["offer_chart"],
        "shortcuts": shortcuts,
        "purchases_enabled": summary["purchases_enabled"],
    })
    return context
