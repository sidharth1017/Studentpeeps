from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re

class GetPhoneView(View):
    def get(self, request):
        return render(request, 'account/getPhoneNo.html')

    def post(self, request):
        identifier = request.POST['identifier']

        if re.match(r'^\d{10}$', identifier):
            request.session['phone'] = identifier
            return redirect('/account/v2/verify')
        else:
            messages.error(request, "Enter a valid phone number.")
            return redirect('/account/v2/phone')
