from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify
from django import forms
from django.utils import timezone
from django.utils.html import format_html
import json

class OfferCategory(models.TextChoices):
    EDUCATION = 'education', 'Education'
    TECH = 'tech', 'Tech'
    FASHION = 'fashion', 'Fashion'
    TRAVEL = 'travel', 'Travel'
    FOOD_DRINK = 'food_drink', 'Foods and Drinks'
    HEALTH_BEAUTY = 'health_beauty', 'Health and Beauty'
    BOOKS_STATIONARY = 'books_stationary', 'Books and Stationary'
    HOME_UTILITIES = 'home_utilities', 'Home and Utilities'
    UNCATEGORIZED = 'uncategorized', 'Uncategorized'

class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/')
    thumbnail_image = models.ImageField(upload_to='brand_thumbnails/', blank=True)
    about = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Brands Onboard"

class Offer(models.Model):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='offers')
    custom_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, default="")
    category = models.ForeignKey('Category', blank=True, related_name='offers', default=OfferCategory.UNCATEGORIZED, on_delete=models.SET_DEFAULT)
    thumbnail_image = models.ImageField(upload_to='exclusive_thumbnails/')
    additional_images = models.JSONField(blank=True, default=list)
    about = models.TextField()
    tnc = models.TextField()
    redemption = models.TextField(blank=True, default="")
    background_color = models.CharField(max_length=250, default='#ffffff')
    codes = models.JSONField(blank=True, default=list)
    offer_link = models.URLField(blank=True, default="")
    isStaticCode = models.BooleanField(default=True)
    isExclusive = models.BooleanField(default=True)
    isLoginRequired = models.BooleanField(default=False)
    isRedirectLogin = models.BooleanField(default=False)
    sorting = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.custom_id

class OfferSEO(models.Model):
    offer = models.OneToOneField('Offer', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    og_image = models.ImageField(upload_to='seo_og_images/', blank=True, default="")
    keywords = models.JSONField(blank=True, default=list)
    class Meta:
        verbose_name_plural = "Offers - SEO"  

class OfferCodeForUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    assigned_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "User Codes - Offer"

class RedeemedCodes(models.Model):
    offer_custom_id = models.CharField(max_length=100, unique=True)
    redeemed_codes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Redeemed Codes"

    def add_code(self, code):
        now = timezone.now().isoformat()
        self.redeemed_codes.append({code: now})
        self.save()

class Category(models.Model):
    category_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    sorting = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.JSONField(blank=True, default=list)
    og_image = models.ImageField(upload_to='category_og_images/', blank=True, default="")
    isVisible = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('CategoryPage', args=[self.category_id])

    class Meta:
        verbose_name_plural = "Categories"

class OfferDailyAnalytics(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    offers_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.date} - {len(self.offers_data)} offers"

    class Meta:
        verbose_name_plural = "Offers Analytics"