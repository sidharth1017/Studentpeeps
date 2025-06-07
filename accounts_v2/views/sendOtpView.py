# views.py
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from accounts_v2.models import Register
from accounts_v2.communication import send_otp_sms, send_otp_sms_via_AWS_SNS
import random

class SendOtpView(View):
    def get(self, request):
        phone = request.session.get('phone')
        if not phone:
            return redirect('/account/v2/identify')

        if not request.session.get('studentpeepsV2'):
            otp = str(random.randint(100000, 999999))
            print(otp, "otppp")
            hashed_otp = make_password(otp)
            request.session['studentpeepsV2'] = hashed_otp        
        masked_phone = phone[:2] + 'X' * 6 + phone[-2:]

        # if not send_otp_sms_via_AWS_SNS(phone, otp):
        #     messages.error(request, "Failed to send OTP. Please try again.")
        #     return redirect('/account/v2/identify')

        return render(request, 'account/sendOtp.html', {'phone': masked_phone})

    def post(self, request):
        input_otp = request.POST['otp']
        stored_hashed_otp = request.session.get('studentpeepsV2')

        if stored_hashed_otp and check_password(input_otp, stored_hashed_otp):
            phone = request.session.get('phone')

            try:
                register = Register.objects.get(phone=phone)
                user = register.user
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user)
                return redirect('/')
            except Register.DoesNotExist:
                if request.session.get('email'):
                    return redirect('/account/v2/your-details')
                else:
                    return redirect('/account/v2/security')

        else:
            messages.error(request, "Invalid OTP.")
            return redirect('/account/v2/verify')

