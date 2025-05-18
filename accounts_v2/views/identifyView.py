from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re

from django.http import JsonResponse
import re
from ..models import Register, Register
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login

class IdentifyView(View):
    def get(self, request):
        request.session.pop('studentpeepsV2', None)
        request.session.pop('email', None)
        request.session.pop('password', None)
        return render(request, 'account/identify.html')

    def post(self, request):
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        if re.match(r'^\d{10}$', identifier):
            request.session['phone'] = identifier
            return JsonResponse({'next': 'otp'})

        elif re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            request.session['email'] = identifier

            if not password:
                return JsonResponse({'next': 'password'})

            else:
                try:
                    user_obj = User.objects.get(email=identifier)
                    if check_password(password, user_obj.password):
                        request.session['user_id'] = user_obj.id
                        user_obj.backend = 'django.contrib.auth.backends.ModelBackend'

                        login(request, user_obj)
                        return JsonResponse({'next': '/'})
                    else:
                        return JsonResponse({'next': None, 'message': 'Incorrect password'})
                except User.DoesNotExist:
                    return JsonResponse({'next': '/account/v2/phone'})

        return JsonResponse({'next': None, 'message': 'Enter a valid email or phone number'})

