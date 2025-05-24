from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re
from django.contrib.auth.hashers import check_password

class EnterPasswordView(View):
    def get(self, request):
        return render(request, 'account/enter_password.html')

    def post(self, request):
        email = request.session.get('email')
        password = request.POST['password']

        try:
            user = Register.objects.get(user__email=email)
            if check_password(password, user.user.password):
                request.session['user_id'] = user.id
                return redirect('/')
            else:
                messages.error(request, "User with this email already exists. Please log in.")
                return redirect('/account/v2/identify')
        except Register.DoesNotExist:
            request.session['password'] = password
            return redirect('/account/v2/your-details')

