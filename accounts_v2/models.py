from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Register(models.Model):
    """Profile for someone who signed up with email or phone OTP."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="", null=True, blank=True)
    firstname = models.CharField(max_length=100, default="", blank=True)
    lastname = models.CharField(max_length=100, default="", blank=True)
    gender = models.CharField(max_length=100, default="", blank=True)
    birthday = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=200, default="", blank=True)
    institution_email = models.CharField(max_length=200, default="", blank=True)
    graduation_year = models.CharField(max_length=100, default="", blank=True)
    collegeId = models.ImageField(upload_to='collegeidcards/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.email or self.phone or self.firstname or str(self.user_id)

    class Meta:
        verbose_name = "Register"
        verbose_name_plural = "Register"
