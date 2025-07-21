from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import View
from ..tasks import send_email
from accounts_v2.communication import send_welcome_email
from accounts_v2.models import Register
from django.db.models import Q
from django.http import HttpResponseForbidden


class UploadEmail(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'uploademail.html')

    def post(self, request):
        messages = None 
        email = request.POST['email']
        register = Register.objects.get(Q(user__username=email) | Q(institution_email=email))
        user = register.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        if not register.is_verified:
            register.is_verified = True
            user.is_active = True
            register.save()
            user.save()
            message = render_to_string('emailers/signup_email_body.html', {'fname': register.firstname})
            send_welcome_email(subject=f"Welcome to Studentpeeps!", email=email, message=message)
            messages = "User is now verified and welcome mail sent to thier email."
        else:
            messages = "User is already verified!"
        return render(request, 'uploademail.html', {'message': messages})
