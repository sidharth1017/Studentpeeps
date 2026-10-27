from django.urls import path

from accounts_v2.views import identify_view, logout_view, myaccount_view, resend_otp_view, verify_view

urlpatterns = [
    path("identify", identify_view.IdentifyViewV2.as_view(), name="IdentifyViewV2"),
    path("verify", verify_view.VerifyViewV2.as_view(), name="VerifyViewV2"),
    path("resend", resend_otp_view.ResendOtpView.as_view(), name="resend_otp"),
    path("myaccount/", myaccount_view.myaccount, name="myaccount"),
    path("logout/", logout_view.Logout.as_view(), name="logout"),
]
