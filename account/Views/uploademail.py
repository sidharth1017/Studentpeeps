from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import View
from ..tasks import send_email
from accounts_v2.communication import send_welcome_email
from accounts_v2.models import Register, RejectedUsers, UnVerifiedIdUpload
from django.db.models import Q
from django.http import HttpResponseForbidden


class VerifyUploadEmailUsers(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'uploademail.html')

    def post(self, request):
        messages = [] 
        email = request.POST['email']

        try:
            register = Register.objects.get(Q(user__username=email) | Q(institution_email=email))
            user = register.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            if not register.is_verified:
                register.is_verified = True
                register.save()
                messages = ["User is now verified"]
            elif not user.is_active:
                user.is_active = True
                user.save()
            mail_body = render_to_string('emailers/signup_email_body.html', {'fname': register.firstname})
            send_welcome_email(subject=f"Welcome to Studentpeeps!", email=email, message=mail_body)

            messages.append("Welcome mail sent to their email.")
        except Register.DoesNotExist:
            try:
                unverified_user = UnVerifiedIdUpload.objects.get(Q(user__username=email) | Q(email=email))
                user = unverified_user.user
                register = Register(user=unverified_user.user, phone=unverified_user.phone, firstname=unverified_user.firstname, lastname=unverified_user.lastname, gender=unverified_user.gender, birthday=unverified_user.birthday, collegeId=unverified_user.collegeId)
                register.is_verified = True
                register.save()
                user.is_active = True
                user.save()
                unverified_user.delete()
                mail_body = render_to_string('emailers/signup_email_body.html', {'fname': unverified_user.firstname})
                send_welcome_email(subject=f"Welcome to Studentpeeps!", email=email, message=mail_body)

                messages.append("Welcome mail sent to their email.")
            except UnVerifiedIdUpload.DoesNotExist:
                messages.append("User not found!")
                return render(request, 'uploademail.html', {'messages': messages})

        return render(request, 'uploademail.html', {'messages': messages})

class RejectUploadEmailUser(View):
    def post(self, request):
        messages = [] 
        email = request.POST['email']
        register = None
        user = None

        try:
            register = Register.objects.get(Q(user__username=email) | Q(institution_email=email))
            user = register.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'     
            messages.append("User is rejected from Register!") 
        except Register.DoesNotExist:
            try:
                register = UnVerifiedIdUpload.objects.get(Q(user__username=email) | Q(email=email))
                user = register.user
                messages.append("User is rejected from UnVerifiedIdUpload!")             
            except UnVerifiedIdUpload.DoesNotExist:
                messages.append("User not found!")
                return render(request, 'uploademail.html', {'messages': messages})

        RejectedUser = RejectedUsers(
            user=user,
            phone=register.phone,
            firstname=register.firstname,
            lastname=register.lastname,
            gender=register.gender,
            birthday=register.birthday,
            collegeId=register.collegeId
        )
        RejectedUser.save()

        user.is_active = False
        user.save()
        register.delete()

        message = render_to_string('emailers/user_rejection_email_body.html', {'fname': register.firstname})
        send_welcome_email(subject="Action Needed: Reapply for Studentpeeps Verification", email=email, message=message)

        messages.append("Email sent to user about rejection and user is now inactive.")
        return render(request, 'uploademail.html', {'messages': messages})


class VerifyUploadPhoneUsers(View):
    def post(self, request):
        messages = []
        phone = request.POST['phone']
        register = Register.objects.get(phone=phone)
        user = register.user

        if not register.is_verified:
            register.is_verified = True
            user.is_active = True
            register.save()
            user.save()
            # Send SMS CODE HERE
            messages = "User is now verified and welcome SMS sent to their phone."
        else:
            messages = "User is already verified!"
        return render(request, 'uploademail.html', {'message': messages})
