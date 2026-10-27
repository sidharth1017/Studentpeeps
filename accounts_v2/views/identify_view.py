from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import JsonResponse
import re


class IdentifyViewV2(View):
    def get(self, request):
        request.session.pop('studentpeepsV2', None)
        request.session.pop('email', None)
        request.session.pop('phone', None)
        request.session['next_url'] = request.GET.get('next')
        return render(request, "pages/account/login_or_signup.html")

    def post(self, request):
        identifier = (request.POST.get('identifier') or '').strip()
        next_param = request.GET.get('next') or request.session.get('next_url')

        if re.match(r'^\d{10}$', identifier):
            request.session['phone'] = identifier
            return redirect(f'/account/verify?next={next_param}' if next_param else '/account/verify')

        if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            request.session['email'] = identifier
            return redirect(f'/account/verify?next={next_param}' if next_param else '/account/verify')

        return JsonResponse({'next': None, 'message': 'Enter a valid email or phone number'})
