from django.contrib import admin
from django.urls import path
from . import views

admin.site.site_header = "Login to Student Peeps"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Welcome to Student Peeps Dashboard"

urlpatterns = [
    path('', views.Home.as_view(), name="Home"),
    path('ourstory/', views.OurStory.as_view(), name="OurStory"),
    path('verification-message/',
         views.VerificationMessage.as_view(), name="Verificationmsg"),
    path('google-verification-message/',
         views.GoogleVerifyMessage.as_view(), name="GoogleVerificationmsg"),
    path('upload-message/', views.UploadMessage.as_view(), name="Uploadmsg"),
    path('google-verified/', views.GoogleVerification.as_view(), name="GoogleVerification"),
    path('contactus/', views.ContactUs.as_view(), name="ContactUs"),
    path('faq/', views.FAQ.as_view(), name="Faq"),
    path('privacypolicy/', views.Privacy.as_view(), name="PrivacyPolicy"),
    path('request-your-fav-brand/', views.Favorite.as_view(), name="Favroiute"),
    path('course-application/', views.Course.as_view(), name="Course"),
    path('resource/', views.Tools.as_view(), name="Resource"),
    path('subscribe', views.SubscribeView.as_view(), name="SubscribeView"),
    path('unsubscribe', views.UnSubscribeView.as_view(), name="UnSubscribeView"),
    path('community/', views.Community.as_view(), name="Community"),
    path('all/', views.All.as_view(), name="All"),
    path('tech/', views.Tech.as_view(), name="Tech"),
#     path('entertainment/', views.Entertainment.as_view(), name="Entertainment"),
    path('foodsanddrinks/', views.FoodsAndDrinks.as_view(), name="FoodsAndDrinks"),
    path('travel/', views.Travel.as_view(), name="Travel"),
    path('healthandbeauty/', views.HealthAndBeauty.as_view(), name="HealthAndBeauty"),
    path('edtech/', views.Edtech.as_view(), name="Edtech"),
    path('booksandstationary/', views.BooksAndStationary.as_view(), name="BooksAndStationary"),
    path('homeandutilities/', views.HomeAndUtilities.as_view(), name="HomeAndUtilities"),
    path('fashion/', views.Fashion.as_view(), name="Fashion"),
    path('exclusive/', views.Exclusive.as_view(), name="Exclusive"),
    path('nonexclusive/', views.NonExclusive.as_view(), name="NonExclusive"),
    path('id-verification-message/',
         views.IdVerificationMessage.as_view(), name="IdVerificationMessage"),

#     path('paymentuser/', views.paymentuser, name='paymentuser'),
]

