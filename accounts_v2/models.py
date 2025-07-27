from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
<<<<<<< Updated upstream
<<<<<<< Updated upstream
class AbandonedSignup(models.Model):
    identifier = models.CharField(max_length=1000, default="", null=True, blank=True)
    firstname = models.CharField(max_length=100, default="", null=True, blank=True)
    lastname = models.CharField(max_length=100, default="", null=True, blank=True)
    gender = models.CharField(max_length=100, default="", null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.identifier    

    class Meta:
        verbose_name_plural = "Abandoned Signups"     
=======
=======
>>>>>>> Stashed changes
# class Register(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=15, unique=True)
#     gender = models.CharField(max_length=100)
#     is_verified = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return self.user.email    

#     class Meta:
#         verbose_name_plural = "Register"   
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

class Register(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default="", null=True, blank=True)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    firstname = models.CharField(max_length=100, default="", blank=True)
    lastname = models.CharField(max_length=100, default="", blank=True)
    gender = models.CharField(max_length=100, default="", blank=True)
    birthday = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=200, default="", blank=True)
    institution_email = models.CharField(max_length=200, default="", blank=True)
    graduation_year = models.CharField(max_length=100, default="", blank=True)
=======
=======
>>>>>>> Stashed changes
    firstname = models.CharField(max_length=100, default="")
    lastname = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=100, default="")
    birthday = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=200, default="")
    institution_email = models.CharField(max_length=200, default="")
    graduation_year = models.CharField(max_length=100, default="")
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    collegeId = models.ImageField(upload_to='collegeidcards/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.firstname    

    class Meta:
        verbose_name_plural = "Register"       


class UnVerified(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=1000, default="", null=True, blank=True)
    phone = models.CharField(max_length=15, default="", null=True, blank=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=200)
    institution_email = models.CharField(max_length=200)
    graduation_year = models.CharField(max_length=100)
    collegeId = models.ImageField(upload_to='collegeidcards/', null=True, blank=True)
    verification_url = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.institution_email

    class Meta:
        verbose_name_plural = "Unverified Users"      