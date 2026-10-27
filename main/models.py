from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.

class Contact(models.Model):
    email = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50, default="")
    message = models.CharField(max_length=1000, default="")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def contact(self):
        self.save()

class RequestBrand(models.Model):
    name = models.CharField(max_length=50, default="")
    email = models.CharField(max_length=50, default="")
    brandname = models.CharField(max_length=100, default="")
    brandsite = models.CharField(max_length=500)
    want = models.CharField(max_length=1000, default="")

    def __str__(self):
        return self.brandname

    def requestbrand(self):
        self.save()
        
class Foundation(models.Model):
    name = models.CharField(max_length=50, default="")
    collegename = models.CharField(max_length=50, default="")
    linkedinurl = models.CharField(max_length=5000, default="")
    email = models.CharField(max_length=50, default="")
    coursename = models.CharField(max_length=100, default="")
    courselink = models.CharField(max_length=500)
    desc = models.CharField(max_length=1000, default="")

    def __str__(self):
        return self.coursename

    def foundation(self):
        self.save()

CHOICES = [('Y','Yes'),('N','No')]
class Resource(models.Model):  
    email = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=12, default="")
    college = models.CharField(max_length=3, choices=CHOICES, default=1)

    def __str__(self):
        return self.email

    def resource(self):
        self.save()


class Brand(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Subscribe(models.Model):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email

class Homepage(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    )

    layout_type = models.CharField(max_length=100, default="")
    position = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    data = models.JSONField(default=dict, blank=True)   # normal layouts
    custom_html = models.TextField(blank=True, null=True)  # custom layout HTML

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.layout_type} ({self.position})"

class PromoStripBanner(models.Model):
    """Top announcement strip (site-wide). Highest-priority enabled row in its schedule window wins."""

    name = models.CharField(max_length=120, help_text="Internal label (not shown on site).")
    is_enabled = models.BooleanField(default=True)
    is_fallback = models.BooleanField(
        default=False,
        help_text="Unused (kept for older rows). All banners compete on priority and schedule only.",
    )
    message = models.CharField(max_length=500)
    cta_label = models.CharField(max_length=80, verbose_name="CTA link text")
    cta_href = models.CharField(max_length=500, verbose_name="CTA URL")
    background_color = models.CharField(max_length=7, default="#14172F")
    text_color = models.CharField(max_length=7, default="#FFFFFF")
    cta_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Leave blank to match text colour.",
    )
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional. Leave empty to start immediately (when enabled).",
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional. Leave empty to run indefinitely (until disabled).",
    )
    priority = models.IntegerField(
        default=0,
        help_text="Higher number wins when multiple banners are active.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-id"]
        verbose_name = "Promo strip banner"
        verbose_name_plural = "Promo strip banners"

    def __str__(self):
        return self.name


class HomepageSection(models.Model):
    """Visibility and copy for a homepage merchandising block."""

    SECTION_STUDENT_FAVOURITES = "student_favourites"
    SECTION_POPULAR_WEEK = "popular_this_week"
    SECTION_CHOICES = (
        (SECTION_STUDENT_FAVOURITES, "Student favourites (hero panel)"),
        (SECTION_POPULAR_WEEK, "Popular this week"),
    )

    section_key = models.CharField(max_length=40, choices=SECTION_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=True)
    title = models.CharField(max_length=120, blank=True, help_text="Blank = default title on site.")
    subtitle = models.CharField(max_length=255, blank=True)
    cta_label = models.CharField(max_length=80, blank=True, help_text="Footer button (hero panel only).")
    cta_href = models.CharField(max_length=500, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Homepage section"
        verbose_name_plural = "Homepage sections"

    def __str__(self):
        return self.get_section_key_display()


class HomepageFeaturedSku(models.Model):
    """One SKU slot in a homepage section (order controlled by sort_order)."""

    section = models.ForeignKey(
        HomepageSection,
        on_delete=models.CASCADE,
        related_name="featured_skus",
    )
    sku = models.CharField(max_length=100, help_text="Provider product SKU, e.g. EGVGBPVRC001")
    display_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional override; blank uses brand name from catalog.",
    )
    subtitle = models.CharField(
        max_length=120,
        blank=True,
        help_text='Short line under the name (e.g. "Movie nights").',
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_enabled = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["section", "sort_order", "id"]
        verbose_name = "Homepage featured SKU"
        verbose_name_plural = "Homepage featured SKUs"

    def __str__(self):
        return f"{self.section.section_key}: {self.sku}"


class PolicyPage(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()                             
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title