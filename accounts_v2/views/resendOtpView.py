# views.py
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from ..communication import send_otp_sms
import random

class ResendOtpView(View):
    def get(self, request):
        phone = request.session.get('phone')
        if not phone:
            return redirect('/account/v2/identify')

        otp = str(random.randint(100000, 999999))
        hashed_otp = make_password(otp)
        request.session['studentpeepsV2'] = hashed_otp

        print("Resent OTP:", otp)

        # Try sending via SMS
        # if not send_otp_sms(phone, otp):
        #     messages.error(request, "Failed to resend OTP. Please try again.")
        # else:
        #     messages.success(request, "OTP resent successfully.")

        return redirect('/account/v2/verify')
