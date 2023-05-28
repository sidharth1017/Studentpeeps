from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.contrib import messages
from ..models import *

class Register(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        Email = request.POST['email']
        Password = request.POST['password']
        if Signup.objects.filter(email=Email).exists() and Yourdetail.objects.filter(email=Email).exists() and Signup.objects.filter(password=Password):  
            request.session['email'] = Email
            request.session['password'] = Password          
            return redirect('/account/signup/')
        elif Signup.objects.filter(email=Email).exists():
            Signup.objects.filter(email=Email).delete()
            signup = Signup(email=Email, password=Password)
            signup.save()
            request.session['email'] = Email
            request.session['password'] = Password
            print(Password)
            print(type(Password))
            return redirect('/account/yourdetail/') 
        else:
            if Registers.objects.filter(username=Email).exists() or User.objects.filter(username=Email).exists():
                messages.error(request, "Looks like you're already a Peep, click on Log in below and enjoy life🙃")
                return redirect('/account/register/')
            elif Registers.objects.filter(email=Email).exists() or User.objects.filter(email=Email).exists():
                messages.error(request, 'Email is already Taken')
                return redirect('/account/register/')
            else:
                signup = Signup(email=Email, password=Password)
                signup.save()
                request.session['email'] = Email
                request.session['password'] = Password
                return redirect('/account/yourdetail/')
            