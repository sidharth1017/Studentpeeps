# views.py
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from accounts_v2.models import Register
from accounts_v2.communication import send_otp,send_otp_email
import random
from django.db.models import Q
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme
from giftcard.services.cart_service import stash_guest_cart_session_for_login
from accounts_v2.flash_messages import discard_checkout_flash_messages


def _store_next_url(request):
    next_param = request.GET.get('next')
    if next_param:
        request.session['next_url'] = next_param


def _safe_next_redirect(request, fallback='/'):
    next_url = request.session.pop('next_url', None) or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback)


def _login_and_redirect(request, user):
    stash_guest_cart_session_for_login(request)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return _safe_next_redirect(request)


class VerifyViewV2(View):
    def get(self, request):
        phone = request.session.get('phone')
        email = request.session.get('email')
        if not phone and not email:
            return redirect('/account/identify')

        discard_checkout_flash_messages(request)
        _store_next_url(request)

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
                success, error_handled = send_otp(request, phone, otp)
                if not success:
                    if not error_handled:
                        messages.error(request, "Failed to send OTP. Please try again.")
                    return redirect('/account/identify')
            if email:
                try:
                    message = render_to_string(
                        'emailers/otp_email_body.html', {'otp': otp})
                    if not send_otp_email(email, otp, message):
                        messages.error(request, "Failed to send OTP. Please try again.")
                        return redirect('/account/identify')
                except Exception as e:
                    print(f"Error sending OTP email: {e}")
                    messages.error(request, "Something went wrong. Please try again.")
                    return redirect('/account/identify')

        return render(request, "pages/account/verify_otp.html", {"phone": masked_details})

    def post(self, request):
        input_otp = request.POST.get('otp', '')
        stored_hashed_otp = request.session.get('studentpeepsV2')

        if stored_hashed_otp and check_password(input_otp, stored_hashed_otp):
            phone = request.session.get('phone')
            email = request.session.get('email')
            _store_next_url(request)

            try:
                if phone:
                    register = Register.objects.get(phone=phone)
                    return _login_and_redirect(request, register.user)

                elif email:
                    register = Register.objects.get(
                        Q(user__username=email) | Q(user__email=email) | Q(institution_email=email)
                    )
                    return _login_and_redirect(request, register.user)

            except Register.DoesNotExist:
                users = User.objects.filter(Q(username=email) | Q(email=email)).distinct()
                if users.exists():
                    user = users.first()
                    if not user.is_active:
                        user.is_active = True
                        user.save()
                        response = _login_and_redirect(request, user)
                        request.session['user_id'] = user.id
                        return response
                    return _login_and_redirect(request, user)
                else:
                    user = User.objects.create_user(username=phone or email, email=email or '')
                    register = Register(user=user, phone=phone)
                    register.is_verified = True
                    register.save()
                    user.save()

                    response = _login_and_redirect(request, user)
                    request.session['user_id'] = register.id
                    return response
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('/account/verify')