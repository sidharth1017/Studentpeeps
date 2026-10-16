from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

class Communication(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]

    SERVICE_CHOICES_SMS = [
        ('twilio', 'Twilio'),
        ('sns', 'AWS SNS'),
    ]

    SERVICE_CHOICES_EMAIL = [
        ('hi@studentpeeps.club', 'hi@studentpeeps.club'),
        ('ayush@studentpeeps.club', 'ayush@studentpeeps.club'),
        ('sidharth@studentpeeps.club', 'sidharth@studentpeeps.club'),
    ]

    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, unique=True)
    service = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.channel.upper()} via {self.service}"
    
    def get_available_choices(self):
        if self.channel == 'sms':
            return dict(self.SERVICE_CHOICES_SMS)
        if self.channel == 'email':
            return dict(self.SERVICE_CHOICES_EMAIL)

class OTPSendLog(models.Model):
    phone = models.CharField(max_length=15)
    date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('phone', 'date')

    def __str__(self):
        return f"{self.phone} - {self.date} : {self.count} times"


class GiftCardSettings(models.Model):
    """
    Single-row switchboard for gift card purchasing (edit it in the admin under Utilities).

    When `purchases_enabled` is off, customers can still pay, but no order is sent to
    Woohoo. The order is parked as "on hold" and the customer sees a message that it
    could not be processed yet.
    """
    DEFAULT_HOLD_MESSAGE = (
        "We can't issue gift cards right now, so your order is on hold. Your payment is safe. "
        "If you don't receive your gift card within 1 hour, your refund will be started automatically. "
        "You can also contact our support team any time."
    )

    purchases_enabled = models.BooleanField(
        default=True,
        verbose_name="Gift card buying enabled",
        help_text="Turn OFF to stop sending orders to Woohoo. Payments still work; paid orders are put on hold.",
    )
    hold_message = models.TextField(
        blank=True,
        default=DEFAULT_HOLD_MESSAGE,
        help_text="Shown to customers whose order is on hold. Leave blank to use the default text.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gift card setting"
        verbose_name_plural = "Gift card settings"

    def __str__(self):
        return "Gift card buying is " + ("ON" if self.purchases_enabled else "OFF")

    def save(self, *args, **kwargs):
        self.pk = 1  # always one row
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def purchases_are_enabled(cls):
        return cls.load().purchases_enabled

    @classmethod
    def customer_hold_message(cls):
        return cls.load().hold_message.strip() or cls.DEFAULT_HOLD_MESSAGE


class PaymentMethodOption(models.Model):
    """
    One row per payment method on the checkout (edit under Utilities > Payment method options).
    Controls whether it is shown, its order, its text, and the price adjustment for using it.
    """
    METHOD_CHOICES = [
        ("upi", "UPI"),
        ("card", "Credit / Debit card"),
        ("netbanking", "Net banking"),
        ("wallet", "Wallets"),
        ("emi", "EMI"),
        ("paylater", "Pay later"),
    ]

    method = models.CharField(max_length=20, choices=METHOD_CHOICES, unique=True)
    enabled = models.BooleanField(default=True, help_text="Untick to hide this method on checkout.")
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")
    label = models.CharField(max_length=60, blank=True, help_text="Name shown to customers. Blank = default name.")
    description = models.CharField(max_length=140, blank=True, help_text="Line shown under the name. Blank = default text.")
    fee_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        verbose_name="Extra fee %",
        help_text="% added to the order total when the customer pays this way (e.g. 1 = 1% extra).",
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        verbose_name="Discount %",
        help_text="% taken off the order total when the customer pays this way. If both are set, the difference applies.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Payment method option"
        verbose_name_plural = "Payment method options"

    def __str__(self):
        return self.display_label

    @property
    def display_label(self):
        from giftcard.payments.methods import PAY_METHODS
        return self.label.strip() or PAY_METHODS[self.method]["label"]

    @property
    def display_description(self):
        from giftcard.payments.methods import PAY_METHODS
        return self.description.strip() or PAY_METHODS[self.method]["description"]

    @classmethod
    def ensure_defaults(cls):
        """Create any missing method rows (new methods appear automatically)."""
        from giftcard.payments.methods import PAY_METHODS
        existing = set(cls.objects.values_list("method", flat=True))
        for i, (key, meta) in enumerate(PAY_METHODS.items()):
            if key not in existing:
                cls.objects.create(method=key, sort_order=(i + 1) * 10, fee_percent=Decimal(meta["fee"]))

