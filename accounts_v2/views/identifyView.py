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
from django.db.models import Q

class IdentifyView(View):
    def get(self, request):
        request.session.pop('studentpeepsV2', None)
        request.session.pop('email', None)
        request.session.pop('phone', None)
        return render(request, 'account/identify.html')

    def post(self, request):
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        if re.match(r'^\d{10}$', identifier): # Phone number Identifier
            request.session['phone'] = identifier
            return redirect('/account/v2/verify')

        elif re.match(r"[^@]+@[^@]+\.[^@]+", identifier): # Email Identifier
            request.session['email'] = identifier
            return redirect('/account/v2/verify')

        return JsonResponse({'next': None, 'message': 'Enter a valid email or phone number'})

        

