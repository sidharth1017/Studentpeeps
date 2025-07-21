# views.py
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from ..communication import send_otp
import random

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
            masked_details = phone[:2] + 'X' * 6 + phone[-2:]
            success, error_handled = send_otp(request, phone, otp)
            if not success:
                if not error_handled:
                    messages.error(request, "Failed to send OTP. Please try again.")
                return redirect('/account/v2/identify')
        if email:
            name_part, domain = email.split('@')
            if len(name_part) <= 4:
                masked_details = name_part[0] + 'x' * (len(name_part) - 2) + name_part[-1] + '@' + domain
            else:
                masked_details = name_part[:2] + 'x' * (len(name_part) - 4) + name_part[-2:] + '@' + domain   
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
