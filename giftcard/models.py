from django.db import models
from brands_v2.models import Category

# Create your models here.
class Provider(models.Model):
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProviderAuthToken(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    access_token = models.TextField()
    token_type = models.CharField(max_length=20, default="Bearer")
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "is_active")

class ProviderApiLog(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    method = models.CharField(max_length=10)
    url = models.TextField()
    request_headers = models.JSONField()
    request_body = models.JSONField(null=True, blank=True)
    response_status = models.IntegerField()
    response_body = models.JSONField(null=True, blank=True)
    signature = models.CharField(max_length=256, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProviderCategory(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_category_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    canonical_url = models.URLField(null=True, blank=True)
    color_code = models.CharField(max_length=20, null=True, blank=True)
    bg_color_code = models.CharField(max_length=20, null=True, blank=True)
    offer_description = models.TextField(null=True, blank=True)
    meta_index = models.BooleanField(null=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    subcategory_filter = models.BooleanField(default=False)
    subcategories_count = models.IntegerField(default=0)
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "provider_category_id")

class CategoryMapping(models.Model):
    platform_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    provider_category = models.ForeignKey(ProviderCategory, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProviderProduct(models.Model):
    """
    Stores raw product data from provider (Woohoo).
    Data is populated in two phases:
    1. Category → Product List API (light data)
    2. Product Detail API (full enrichment)
    """

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="products"
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    provider_product_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Woohoo product ID from detail API"
    )

    # -----------------------------
    # Basic Info (List + Detail)
    # -----------------------------
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)

    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)

    # -----------------------------
    # Brand Info
    # -----------------------------
    brand_name = models.CharField(max_length=255, blank=True)
    brand_code = models.CharField(max_length=255, blank=True, null=True)
    brand_logo = models.URLField(blank=True)

    # -----------------------------
    # Pricing (List + Detail)
    # -----------------------------
    currency_code = models.CharField(
        max_length=10,
        default="INR"
    )

    currency_symbol = models.CharField(
        max_length=5,
        default="₹"
    )

    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    price_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="SLAB or RANGE"
    )

    denominations = models.JSONField(
        default=list,
        blank=True,
        help_text="Available denominations"
    )

    # -----------------------------
    # Images (List + Detail)
    # -----------------------------
    thumbnail = models.URLField(blank=True)
    mobile_image = models.URLField(blank=True)
    base_image = models.URLField(blank=True)
    small_image = models.URLField(blank=True) 

    # -----------------------------
    # Terms & Expiry (Detail)
    # -----------------------------
    tnc_link = models.URLField(blank=True)
    tnc_content = models.TextField(blank=True)

    expiry_info = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human readable expiry info"
    )

    # -----------------------------
    # Availability & Flags
    # -----------------------------
    in_stock = models.BooleanField(default=True)

    is_digital = models.BooleanField(
        default=True,
        help_text="DIGITAL / PHYSICAL (Woohoo uses DIGITAL)"
    )

    kyc_enabled = models.BooleanField(
        default=False
    )

    disable_cart = models.BooleanField(
        default=False
    )

    # -----------------------------
    # Provider Metadata
    # -----------------------------
    provider_created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    provider_updated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # -----------------------------
    # Sync Tracking
    # -----------------------------
    last_list_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last synced via category-product list API"
    )

    last_detail_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last synced via product detail API"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------------
    # Constraints
    # -----------------------------
    class Meta:
        indexes = [
            models.Index(fields=["provider", "sku"]),
            models.Index(fields=["provider", "provider_product_id"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductOverride(models.Model):
    """
    Platform-level overrides on top of ProviderProduct
    All fields are OPTIONAL.
    """

    product = models.OneToOneField(
        ProviderProduct,
        on_delete=models.CASCADE,
        related_name="override"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    tnc_content = models.TextField(
        null=True,
        blank=True
    )

    margin = models.DecimalField(
        max_digits=6,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Margin percentage or absolute (platform-defined)"
    )

    brand_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    brand_code = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    brand_logo = models.URLField(
        null=True,
        blank=True
    )

    thumbnail = models.URLField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Override for {self.product.sku}"


import uuid
from decimal import Decimal


class Cart(models.Model):
    """
    Single cart per user or guest.
    Products stored inside JSON.
    """

    cart_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    # Guest cart support
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    items = models.JSONField(
        default=list,
        help_text="""
        Example structure:
        [
            {
                "sku": "EGVGBSHSS001",
                "name": "Amazon Pay Gift Card",
                "denomination": "500",
                "quantity": 2,
                "unit_price": "500",
                "margin": "20",
                "final_price": "520"
            }
        ]
        """
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ----------------------------------------
    # Utility Methods
    # ----------------------------------------

    def total_amount(self):
        total = Decimal("0")
        for item in self.items:
            total += Decimal(item["final_price"]) * item["quantity"]
        return total

    def __str__(self):
        return f"Cart {self.cart_id}"


class Order(models.Model):
    """
    Final order after checkout.
    Lifecycle: PENDING → PAYMENT_INITIATED → PAYMENT_CONFIRMED → WOOHOO_PLACED → COMPLETED
                                                               ↘ FAILED
    """

    STATUS_PENDING              = "PENDING"
    STATUS_PAYMENT_INITIATED    = "PAYMENT_INITIATED"
    STATUS_PAYMENT_CONFIRMED    = "PAYMENT_CONFIRMED"
    STATUS_WOOHOO_PLACED        = "WOOHOO_PLACED"
    STATUS_COMPLETED            = "COMPLETED"
    STATUS_FAILED               = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING,           "Pending"),
        (STATUS_PAYMENT_INITIATED, "Payment Initiated"),
        (STATUS_PAYMENT_CONFIRMED, "Payment Confirmed"),
        (STATUS_WOOHOO_PLACED,     "Woohoo Order Placed"),
        (STATUS_COMPLETED,         "Completed"),
        (STATUS_FAILED,            "Failed"),
    ]

    user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    reference_id = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_id = models.CharField(max_length=50, default="woohoo")
    items_snapshot = models.JSONField(default=list)
    status = models.CharField(max_length=30, default=STATUS_PENDING, choices=STATUS_CHOICES)

    # --- Customer info (captured at checkout) ---
    customer_name  = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)

    # --- Payment Gateway ---
    payment_gateway   = models.CharField(max_length=50, default="razorpay")
    gateway_order_id  = models.CharField(max_length=100, blank=True, help_text="e.g. Razorpay order_id")
    gateway_payment_id = models.CharField(max_length=100, blank=True, help_text="e.g. razorpay_payment_id after success")

    # --- Woohoo ---
    woohoo_order_id   = models.CharField(max_length=100, blank=True, help_text="Order ID returned by Woohoo API")
    woohoo_response   = models.JSONField(null=True, blank=True, help_text="Full Woohoo API response")
    is_vouchers_fetched = models.BooleanField(default=False, help_text="True if Activated Cards API has been successfully called")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.reference_id} [{self.status}]"


class PaymentTransaction(models.Model):
    """
    Audit log for every payment gateway event.
    One Order can have multiple transaction attempts.
    """
    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    gateway        = models.CharField(max_length=50)            # e.g. "razorpay"
    gateway_order_id  = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    currency       = models.CharField(max_length=10, default="INR")
    status         = models.CharField(max_length=30, default="INITIATED")
    raw_response   = models.JSONField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PaymentTransaction [{self.gateway}] {self.gateway_payment_id or self.gateway_order_id}"