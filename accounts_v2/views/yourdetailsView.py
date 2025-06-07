from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from ..models import Register
from ..communication import send_welcome_email
from django.template.loader import render_to_string

class YourdetailsView(View):
    def get(self, request):
        return render(request, 'account/name_gender.html')

    def post(self, request):
        name = request.POST['name']
        email = request.session.get('email')
        phone = request.session.get('phone')
        password = request.session.get('password')

        # Create or update the Django User
        user, created = User.objects.get_or_create(email=email)
        user.username = email
        user.email = email
        user.first_name = name
        user.password = make_password(password)  # Update password every time
        user.save()

        # Create or update the Register model
        register, _ = Register.objects.get_or_create(
            user=user,
            defaults={'phone': phone, 'is_verified': True}
        )
        register.phone = phone
        register.is_verified = True
        register.save()

        # Login the user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        message = render_to_string('emailers/signup_email_body.html', {'fname': name})
        send_welcome_email(subject=f"Welcome to the club {name}", email=email, message=message)

        request.session['user_id'] = register.id
        return redirect('/')