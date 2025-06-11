from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class BrandOnboard(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)
    websiteUrl = models.CharField(max_length=300)
    logo = models.ImageField(upload_to='brands_v2/logos')
    thumbnail = models.ImageField(upload_to='brands_v2/thumbnail', blank=True, null=True)
    about = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Brand Onboard"     

class ExclusiveOffer(models.Model):
    brand = models.OneToOneField(BrandOnboard, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=500,blank=True, null=True)  
    thumbnail = models.ImageField(upload_to='brands_v2/exclusiveoffer/thumbnail', blank=True, null=True)
    additionalImage = models.ImageField(upload_to='brands_v2/exclusiveoffer/additionalImage', blank=True, null=True)
    backgroundColor = models.CharField(max_length=7)
    about = RichTextField()
    termsandCondition = RichTextField()
    code = models.JSONField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Exclusive Offers"     
    
class NonExclusiveOffer(models.Model):
    brand = models.OneToOneField(BrandOnboard, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=500)  
    thumbnail = models.ImageField(upload_to='brands_v2/exclusiveoffer/thumbnail')
    additionalImage = models.ImageField(upload_to='brands_v2/exclusiveoffer/additionalImage')
    backgroundColor = models.CharField(max_length=7)
    about = RichTextField()
    termsandCondition = RichTextField()
    offerLink = models.CharField(max_length=300) 

    class Meta:
        verbose_name_plural = "Non Exclusive Offers"   

class Seo(models.Model):
    brand = models.OneToOneField(BrandOnboard, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300)    
    og_title = models.CharField(max_length=200)
    og_description = models.CharField(max_length=300)    
    og_image = models.ImageField(upload_to='brands_v2/seo/ogImage')
    keywords = models.JSONField()

    class Meta:
        verbose_name_plural = "Seo"   