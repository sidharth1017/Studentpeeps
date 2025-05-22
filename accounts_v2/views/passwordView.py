from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re

class EnterPasswordView(View):
    def get(self, request):
        return render(request, 'account/enter_password.html')

    def post(self, request):
        email = request.session.get('email')
        password = request.POST['password']

        try:
            user = Register.objects.get(user__email=email)
            if user.password == password:
                request.session['user_id'] = user.id
                return redirect('/')
            else:
                messages.error(request, "Incorrect password.")
                return redirect('enter_password')
        except Register.DoesNotExist:
            request.session['password'] = password
            return redirect('/account/v2/your-details')

