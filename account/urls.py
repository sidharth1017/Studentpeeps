from django.urls import path, include
from django_email_verification import urls as email_urls
from django.contrib.auth import views as auth_views
from . import views
from .Views import login, logout, register, signup, upload, myaccount, yourdetail, uploademail, verification, send, sendmailtounverifieds, college

urlpatterns = [
    # path('register/', register.Register.as_view(), name='register'),
    # path('yourdetail/', yourdetail.YourDetail.as_view(), name='yourdetail'),
    # path('signup/', signup.SignUp.as_view(), name='signup'),
    # path('upload/', upload.UploadClass.as_view(), name='upload'),
    # path('login/', login.Login.as_view(), name='login'),
    path('logout/', logout.Logout.as_view(), name='logout'),
    # path('email/', include(email_urls)),
    # path('activate/<uidb64>/<token>/<new>', verification.VerificationView.as_view(), name="activate"),
    path('myaccount/', myaccount.myaccount, name="myaccount"),    
    # path('636756-secret-upload-email-page', uploademail.UploadEmail.as_view(), name="Secret Page"),
    # path('send/', send.Send.as_view(), name="send"),
    # path('sendmailtounverifieds/', sendmailtounverifieds.SendMailToUnverifieds.as_view(), name="SendMailToUnverifieds"),
    # path('YourDetail', views.YourDetail, name='YourDetail'),
    # path('send_email', views.sendEmail, name="send_email"),

    # Reset Password Urls
    # path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
    # name="reset_password"),

    # path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"),
    # name="password_reset_done"),

    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"),
    # name="password_reset_confirm"),

    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),
    # name="password_reset_complete"),

    #Data     
    # path('registers-data-1017/', views.Register, name='Register'),
    # path('uploads-data-1017/', views.Uploads, name='Uploads'),

    # Extra
    # path('signupview/', views.SignUpView, name='signupview'),
    # path('college/', college.CollegeView.as_view(), name='CollegeView'),
    # path('test_email/', signup.TestEmail.as_view(), name='TestEmail'),

    # Razorpay
    # path('membership/', views.Membership, name='Membership'),
    # path('razorpay_callback/', views.RazorpayCallback, name='RazorpayCallback'),
    # path('coupon_code/', views.CouponCode, name='CouponCode'),
] 