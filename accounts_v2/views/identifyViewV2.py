from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re

from django.http import JsonResponse
import re
from ..models import AbandonedSignup, Register
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.db.models import Q

class IdentifyViewV2(View):
    def get(self, request):
        request.session.pop('studentpeepsV2', None)
        request.session.pop('email', None)
        request.session.pop('phone', None)
        request.session['next_url'] = request.GET.get('next')
        return render(request, 'account/identify.html')

    def post(self, request):
        identifier = request.POST.get('identifier')
        if not AbandonedSignup.objects.filter(identifier=identifier).exists() and not Register.objects.filter(Q(user__username=identifier) | Q(institution_email=identifier) | Q(phone=identifier)):
            abandonedSignup = AbandonedSignup(identifier=identifier)
            abandonedSignup.save()

        next_param = request.GET.get('next') or request.session.get('next_url')


        if re.match(r'^\d{10}$', identifier): # Phone number Identifier
            request.session['phone'] = identifier
            return redirect(f'/account/v2/verify?next={next_param}' if next_param else '/account/v2/verify')

        elif re.match(r"[^@]+@[^@]+\.[^@]+", identifier): # Email Identifier
            request.session['email'] = identifier
            return redirect(f'/account/v2/verify?next={next_param}' if next_param else '/account/v2/verify')

        return JsonResponse({'next': None, 'message': 'Enter a valid email or phone number'})