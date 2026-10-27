from django.urls import path
from .views import resendOtpView, verifyViewV2, identifyViewV2
from account.Views import myaccount

urlpatterns = [
    path('identify', identifyViewV2.IdentifyViewV2.as_view(), name='IdentifyViewV2'),
    path('verify', verifyViewV2.VerifyViewV2.as_view(), name='VerifyViewV2'),
    path('resend', resendOtpView.ResendOtpView.as_view(), name='resend_otp'),
    path('myaccount/', myaccount.myaccount, name="myaccount"),
]
