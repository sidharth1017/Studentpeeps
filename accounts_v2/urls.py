from django.urls import path, include
from django_email_verification import urls as email_urls
from django.contrib.auth import views as auth_views
from . import views
from .views import identifyView, sendOtpView, securityView, passwordView, yourdetailsView, phoneNoView, resendOtpView, googleAuthView, institutionView, verificationView, collegeView, idUploadView, idCardVerificationMessageView
from account.Views import uploademail, myaccount
urlpatterns = [
    path('identify', identifyView.IdentifyView.as_view(), name='Identify'),
    path('verify', sendOtpView.SendOtpView.as_view(), name='Verify OTP'),
    path('institution', institutionView.InstitutionView.as_view(), name='Insititution'),
    path('upload-college-id', idUploadView.IdUploadView.as_view(), name='College-id-upload'),
    path('college', collegeView.CollegeView.as_view(), name='College'),
    path('setup-password', passwordView.EnterPasswordView.as_view(), name='Password'),
    path('your-details', yourdetailsView.YourdetailsView.as_view(), name='Your Details'),
    path('phone', phoneNoView.GetPhoneView.as_view(), name='Phone'),
    path('resend', resendOtpView.ResendOtpView.as_view(), name='resend_otp'),
    path('activate/<uidb64>/<token>/<new>', verificationView.VerificationView.as_view(), name="activate"),
    path('student-verification-status', idCardVerificationMessageView.IdCardVerificationMessageView.as_view(), name="Verificationmsg"),
    path('myaccount/', myaccount.myaccount, name="myaccount"),
    path('verify-id-upload-user', uploademail.VerifyUploadEmailUsers.as_view(), name="verify_id_upload_user"),
    path('reject-id-upload-user', uploademail.RejectUploadEmailUser.as_view(), name="reject_id_upload_user"),
    path('verify-id-upload-user-phone', uploademail.VerifyUploadPhoneUsers.as_view(), name="verify_id_upload_user_phone"),
    path('reject-id-upload-user-phone', uploademail.RejectUploadPhoneUsers.as_view(), name="reject_id_upload_user_phone"),
]