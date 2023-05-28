from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Registers(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    date = models.CharField(max_length=100, blank=True, null=True)
    month = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=200)
    institution_email = models.CharField(max_length=200)
    graduation_year = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='pics', default="", blank=True, null=True)

    def __str__(self):
        return self.email

class UnVerified(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    date = models.CharField(max_length=100, blank=True, null=True)
    month = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=200)
    institution_email = models.CharField(max_length=200)
    graduation_year = models.CharField(max_length=100)
    verification_url = models.CharField(max_length=500, default="")
    
    def __str__(self):
        return self.email


class Upload(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    date = models.CharField(max_length=100, blank=True, null=True)
    month = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='pics')
    profile_image = models.ImageField(upload_to='pics', default="")

    def __str__(self):
        return self.email

class Signup(models.Model):
    email = models.CharField(max_length=1000)
    password = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.email

    def signup(self):
        self.save()

class Yourdetail(models.Model):
    email = models.CharField(max_length=1000, default="")
    password = models.CharField(max_length=100, default="")
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    date = models.CharField(max_length=100, blank=True, null=True)
    month = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.firstname

    def yourdetail(self):
        self.save()


class College(models.Model):
    name = models.CharField(max_length=500)
    emails = models.JSONField()

    def __str__(self):
        return self.name


class Payment(models.Model):
    payment_status_choices = (
        (1, "SUCCESS"),
        (2, "FAILURE"),
        (3, "PENDING"),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payment_status = models.IntegerField(choices=payment_status_choices, default=3)
    amount = models.FloatField()
    datetime_of_payment = models.DateTimeField(default=timezone.now)

    # Razorpay
    razorpay_order_id = models.CharField(max_length=500, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=500, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.id}"
        