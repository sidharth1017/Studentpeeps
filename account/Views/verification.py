from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.template.loader import render_to_string
from django.views import View
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from ..models import *
from ..tasks import send_welcome_email
from django.http import HttpResponseRedirect, JsonResponse


class VerificationView(View):
    def get(self, request, uidb64, token, new):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user.is_active = True
        if UnVerified.objects.filter(username=user.username).exists():
            profile = UnVerified.objects.get(username=user.username)
            register = Registers(username=profile.username, password=profile.password, email=profile.email, firstname=profile.firstname, lastname=profile.lastname, gender=profile.gender, institution=profile.institution, institution_email=profile.institution_email, graduation_year=profile.graduation_year)
            if new == "new":
                emailDomain = profile.institution_email.split("@")[1]
                college = College(name=profile.institution, emails=[emailDomain])
                college.save()
            register.save()
            user.save()
            emailname = profile.firstname
            pemail = profile.email
            UnVerified.objects.filter(username=profile.username).delete()
            Signup.objects.filter(email=pemail).delete()
            Yourdetail.objects.filter(firstname=emailname).delete()
            user = auth.authenticate(
                username=profile.username, password=profile.password)

            if user is not None:
                auth.login(request, user)
                message = render_to_string(
                    'mail_body2.html', {'fname': emailname})
                send_welcome_email(subject="Welcome to the club + your 🔑", email=pemail, message=message)
                return HttpResponseRedirect("https://studentpeeps.club/?utm_source=verification&utm_medium=email&utm_campaign=signuprate&utm_term=registers")
            else:
                message = render_to_string(
                'mail_body2.html', {'fname': emailname})
                send_welcome_email(subject="Welcome to the club + your 🔑", email=pemail, message=message)
                return HttpResponseRedirect("https://studentpeeps.club/google-verified/?utm_source=google+verification&utm_medium=verification+email&utm_campaign=googlesignups&utm_id=googleuser&utm_term=registers")
                