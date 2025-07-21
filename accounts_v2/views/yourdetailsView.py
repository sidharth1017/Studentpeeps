from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from ..models import Register
from ..communication import send_welcome_email
from django.template.loader import render_to_string
from datetime import datetime

class YourdetailsView(View):
    def get(self, request):
        return render(request, 'account/name_gender.html')

    def post(self, request):
        FirstName = request.POST['fname']
        LastName = request.POST['lname'] 
        Gender = request.POST['Gender']
        dob_str = request.POST.get('dob')

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            dob = None

        request.session['fname'] = FirstName
        request.session['lname'] = LastName
        request.session['gender'] = Gender
        request.session['birthday'] = dob.isoformat() if dob else None
        
        return redirect('/account/v2/institution')