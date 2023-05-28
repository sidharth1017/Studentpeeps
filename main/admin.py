from django.contrib import admin
from .models import RequestBrand, Contact, Foundation, Resource, Brand, Subscribe


# Register your models here.

admin.site.register(Contact)
admin.site.register(RequestBrand)
class FoundationAdmin(admin.ModelAdmin):
    list_display = ('name','collegename','email', 'coursename')
admin.site.register(Foundation, FoundationAdmin)
admin.site.register(Resource)
admin.site.register(Brand)
admin.site.register(Subscribe)
