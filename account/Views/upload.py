from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import auth
from django.views.generic.base import View
from django.contrib import messages
from account.Views import login
from ..models import *
from decouple import config
import razorpay

razorpay_client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))

class UploadClass(View):
    def get(self, request):
        return render(request, 'signup4.html')

    def post(self, request):
        images = request.FILES['image']

        username = request.session.get('email')

        if Yourdetail.objects.filter(email=username).exists():
            yourdetail = Yourdetail.objects.get(email=username)
            Firstname = yourdetail.firstname
            Lastname = yourdetail.lastname
            Password = yourdetail.password
            Gender = yourdetail.gender

        else:
            username = request.session.get('email')
            Firstname = request.session.get('fname')
            Lastname = request.session.get('lname')
            Gender = request.session.get('gender')
            Password = request.session.get('password')


        if User.objects.filter(email=username).exists():
            user = User.objects.get(email=username)                             
        else:
            user = User.objects.create_user(username=username, password=Password, email=username,
                                                first_name=Firstname, last_name=Lastname)
        user.is_active = True
        user.save()

        if UnVerified.objects.filter(email=username).exists():            
            UnVerified.objects.filter(email=username).delete()

        if Upload.objects.filter(email=username).exists():
            Upload.objects.filter(email=username).delete()


        register = Upload(username=username, password=Password, email=username, firstname=Firstname, lastname=Lastname, gender=Gender, image=images)
        register.save()

        if Signup.objects.filter(email=username).exists():
            Signup.objects.filter(email=username).delete()
        if Yourdetail.objects.filter(email=username).exists():
            Yourdetail.objects.filter(email=username).delete()

        google_username = request.session.get('username')
        google_sign_up = request.session.get('google_sign_up')
        if google_sign_up:
            user_login = User.objects.get(username=google_username, email=username)
        else:
            user_login = auth.authenticate(username=username, password=Password)
            
        if user_login is not None:
            auth.login(request, user_login, backend='django.contrib.auth.backends.ModelBackend')
            
        return HttpResponseRedirect("https://studentpeeps.club/?utm_source=verification&utm_medium=email&utm_campaign=signuprate&utm_term=registers")
    