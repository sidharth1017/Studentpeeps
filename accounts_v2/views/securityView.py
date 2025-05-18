from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *
import re
from django.http import JsonResponse

class GetEmailView(View):
    def get(self, request):
        return render(request, 'account/getemail.html')

    def post(self, request):
        request.session['email'] = request.POST.get('email')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect('/account/v2/setup-password')
