from django.db import models

# Create your models here.

class Contact(models.Model):
    email = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50, default="")
    message = models.CharField(max_length=1000, default="")

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
        