import django
from django.shortcuts import render, redirect
from django.views.generic.base import View
from ..models import *

class YourDetail(View):
    def get(self, request):
        return render(request, 'signup2.html')

    def post(self, request):
        Email = request.session.get('email') 
        Password = request.session.get('password')
        FirstName = request.POST['fname']
        LastName = request.POST['lname'] 
        Gender = request.POST['Gender']

        if Yourdetail.objects.filter(email=Email).exists():
            Yourdetail.objects.filter(email=Email).delete()
            yourdetail = Yourdetail(email=Email, password=Password, firstname=FirstName, lastname=LastName, gender=Gender)
            yourdetail.save()
            return redirect('/account/upload/')
        else: 
            yourdetail = Yourdetail(email=Email, password=Password, firstname=FirstName, lastname=LastName, gender=Gender)
            yourdetail.save()

            request.session['fname'] = FirstName
            request.session['lname'] = LastName
            request.session['gender'] = Gender

            return redirect('/account/upload/')
        