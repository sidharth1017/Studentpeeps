from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from ..models import *

class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['email']
        password = request.POST['password']
        next = request.POST['next']

        if UnVerified.objects.filter(username=username).exists() and UnVerified.objects.filter(password=password):
            UnVerified.objects.filter(username=username).delete()
            request.session['email'] = username
            request.session['password'] = password
            return redirect('/account/signup/')

        else:
            user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if next:
                return redirect(f'{next}')
            else:
                return redirect('/')
        else:
            messages.error(
                request, "Looks like you haven't signed up yet or you've entered the wrong password.")
            return redirect('login')
            