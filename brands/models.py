from django.db import models

# Create your models here.

class BrandCode(models.Model):
    brandname = models.CharField(max_length=500)
    codes = models.JSONField()

    def __str__(self):
        return self.brandname

class BrandSearch(models.Model):
    brandname = models.CharField(max_length=500)
    desc = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='brands')

    def __str__(self):
        return self.brandname
