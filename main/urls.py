from django.contrib import admin
from django.urls import path
from . import views

admin.site.site_header = "Login to Student Peeps"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Welcome to Student Peeps Dashboard"

urlpatterns = [
    path('', views.Home.as_view(), name="Home"),
    path('category/<slug:category_id>/', views.CategoryPageView.as_view(), name='CategoryPage'),
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
    path('id-verification-message/',
         views.IdVerificationMessage.as_view(), name="IdVerificationMessage"),
]

