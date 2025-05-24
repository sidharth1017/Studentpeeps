from django.shortcuts import render
from ..models import *
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout

# Create your views here.

def GoogleAuthFun(request):
    next_url = request.GET.get('next')
    if User.objects.filter(email=request.user.email).exists() & Register.objects.filter(user__email=request.user.email).exists():
        if next_url:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect('/')
    else:
        user = User.objects.get(pk=request.user.id)
        logout(request)
        request.session['google_sign_up'] = True
        request.session['username'] = user.email
        request.session['fname'] = user.first_name
        request.session['email'] = user.email
        request.session['password'] = user.password
        return HttpResponseRedirect('/account/v2/phone')
