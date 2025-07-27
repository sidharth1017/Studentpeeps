# views.py
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
from accounts_v2.models import Register
from accounts_v2.communication import send_otp,send_otp_email
import random
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.template.loader import render_to_string

class SendOtpView(View):
    def get(self, request):
        phone = request.session.get('phone')
        email = request.session.get('email')
        if not phone and not email:
            return redirect('/account/v2/identify')

        if phone:
            masked_details = phone[:2] + 'X' * 6 + phone[-2:]
        elif email:
            name_part, domain = email.split('@')
            if len(name_part) <= 4:
                masked_details = name_part[0] + 'x' * (len(name_part) - 2) + name_part[-1] + '@' + domain
            else:
                masked_details = name_part[:2] + 'x' * (len(name_part) - 4) + name_part[-2:] + '@' + domain   


        if not request.session.get('studentpeepsV2'):
            otp = str(random.randint(100000, 999999))
            hashed_otp = make_password(otp)
            request.session['studentpeepsV2'] = hashed_otp      
            if not send_otp(phone, otp):
                messages.error(request, "Failed to send OTP. Please try again.")
                return redirect('/account/v2/identify')  
        masked_phone = phone[:2] + 'X' * 6 + phone[-2:]


        return render(request, 'account/sendOtp.html', {'phone': masked_phone})

    def post(self, request):
        input_otp = request.POST['otp']
        stored_hashed_otp = request.session.get('studentpeepsV2')

        if stored_hashed_otp and check_password(input_otp, stored_hashed_otp):
            phone = request.session.get('phone')
            email = request.session.get('email')

            try:
                register = Register.objects.get(phone=phone)
                user = register.user
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user)
                return redirect('/')
            except Register.DoesNotExist:
                users = User.objects.filter(Q(username=email) | Q(email=email)).distinct()
                if users.exists():
                    user = users.first()
                    if not user.is_active:
                        messages.error(request, "Your account is inactive. Please contact support.")
                        return HttpResponseRedirect('/')
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect('/')
                else:
                    return redirect('/account/v2/your-details')
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('/account/v2/verify')


