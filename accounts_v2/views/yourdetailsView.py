from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from ..models import Register

class YourdetailsView(View):
    def get(self, request):
        return render(request, 'account/name_gender.html')

    def post(self, request):
        name = request.POST['name']
        email = request.session.get('email')
        phone = request.session.get('phone')
        password = request.session.get('password')

        # Create Django User
        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)
        )

        # Create entry in custom Register model
        register = Register.objects.create(
            user=user,
            phone=phone,
            is_verified=True
        )

        # Login the user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        request.session['user_id'] = register.id
        return redirect('/')