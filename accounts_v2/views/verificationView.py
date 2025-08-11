from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.template.loader import render_to_string
from django.views import View
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from account.models import College
from ..models import *
from accounts_v2.communication import send_welcome_email
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login
from account.tasks import send_email


class VerificationView(View):
    def get(self, request, uidb64, token, new):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if(user.is_active):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, "You are already a verified user.")
            return redirect('/')

        user.is_active = True
        
        if UnVerified.objects.filter(institution_email=user.email).exists():
            profile = UnVerified.objects.get(institution_email=user.email)
            register = Register(user=user, phone=profile.phone, firstname=profile.firstname, lastname=profile.lastname, gender=profile.gender, birthday=profile.birthday, institution=profile.institution, institution_email=profile.institution_email, graduation_year=profile.graduation_year)
            register.is_verified = True
            register.save()
            user.save()

            if new == "new":
                emailDomain = profile.institution_email.split("@")[1]
                college = College(name=profile.institution, emails=[emailDomain])
                college.save()
                try:                                   
                    send_email(subject="New Institution Added🎀",
                            email=["sidharthv605@gmail.com", "mittalayush740@gmail.com"], message=f"Name: {profile.institution} \nEmail: {profile.institution_email}")
                except Exception as e:
                    print(f"Email sending failed: {e}")

            emailname = profile.firstname

            UnVerified.objects.filter(institution_email=profile.institution_email).delete()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            try:
                message = render_to_string('emailers/signup_email_body.html', {'fname': emailname})
                send_welcome_email(subject=f"Welcome to Studentpeeps!", email=profile.institution_email, message=message)
            except Exception as e:
                print(f"Email sending failed: {e}")

            request.session['user_id'] = register.id
            return redirect('/')