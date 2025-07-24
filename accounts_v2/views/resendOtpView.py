# views.py
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from ..communication import send_otp,send_otp_email
import random
from django.template.loader import render_to_string

class ResendOtpView(View):
    def get(self, request):
        phone = request.session.get('phone')
        email = request.session.get('email')
        if not phone and not email:
            return redirect('/account/v2/identify')

        otp = str(random.randint(100000, 999999))
        hashed_otp = make_password(otp)
        request.session['studentpeepsV2'] = hashed_otp    

        if phone:
            success, error_handled = send_otp(request, phone, otp)
            if not success:
                if not error_handled:
                    messages.error(request, "Failed to send OTP. Please try again.")
                return redirect('/account/v2/identify')
        if email:
            try:
                message = render_to_string(
                    'emailers/otp_email_body.html', {'otp': otp})
                if not send_otp_email(email, otp, message):
                    messages.error(request, "Failed to send OTP. Please try again.")
                    return redirect('/account/v2/identify')
            except Exception as e:
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('/account/v2/identify')

        return redirect('/account/v2/verify')
