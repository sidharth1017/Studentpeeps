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

            if phone:
                print(otp, "asdfhkj")
                # success, error_handled = send_otp(request, phone, otp)
                # if not success:
                #     if not error_handled:
                #         messages.error(request, "Failed to send OTP. Please try again.")
                #     return redirect('/account/v2/identify')
            if email:
                try:
                    print(otp, "asdfhkj")
                    # message = render_to_string(
                    #     'emailers/otp_email_body.html', {'otp': otp})
                    # if not send_otp_email(email, otp, message):
                    #     messages.error(request, "Failed to send OTP. Please try again.")
                    #     return redirect('/account/v2/identify')
                except Exception as e:
                    messages.error(request, "Something went wrong. Please try again.")
                    return redirect('/account/v2/identify')

        return render(request, 'account/sendOtp.html', {'phone': masked_details})

    def post(self, request):
        input_otp = request.POST['otp']
        stored_hashed_otp = request.session.get('studentpeepsV2')

        if stored_hashed_otp and check_password(input_otp, stored_hashed_otp):
            phone = request.session.get('phone')
            email = request.session.get('email')
            next_url = request.session.pop('next_url', None) or '/'

            try:
                if phone:
                    register = Register.objects.get(phone=phone)
                    user = register.user
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    if not register.is_verified:
                        messages.error(request, "Your account is inactive. Please contact support.")
                        return HttpResponseRedirect('/')
                    login(request, user)
                    return redirect(next_url)

                elif email:
                    register = Register.objects.get(Q(user__username=email) | Q(institution_email=email))
                    user = register.user
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    if not register.is_verified:
                        messages.error(request, "Your account is inactive. Please contact support.")
                        return HttpResponseRedirect('/')
                    login(request, user)
                    return redirect(next_url)

            except Register.DoesNotExist:
                users = User.objects.filter(Q(username=email) | Q(email=email)).distinct()
                if users.exists():
                    user = users.first()
                    if not user.is_active:
                        return redirect('/account/v2/your-details')
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect(next_url)
                else:
                    return redirect('/account/v2/your-details')
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('/account/v2/verify')


