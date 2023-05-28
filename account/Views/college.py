from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.urls import reverse
from ..utils import token_generator
from ..tasks import send_email
from ..models import *
from django.contrib import messages

class CollegeView(View):
    def post(self, request):
        collegeName = request.POST['institution_name']
        collegeEmail = request.POST['institution_email']
        graduation_year = request.POST['graduation_year']        
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
            request.session['institution_email'] = collegeEmail



        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username) 
            User.objects.get(username=username).delete()
                
            user = User.objects.create_user(username=username, password=Password, email=collegeEmail,
                                                    first_name=Firstname, last_name=Lastname)
            
        elif User.objects.filter(email=username).exists():
            user = User.objects.get(email=username) 
            User.objects.get(email=username).delete()
                
            user = User.objects.create_user(username=username, password=Password, email=collegeEmail,
                                                    first_name=Firstname, last_name=Lastname)
                                                
        else:
            user = User.objects.create_user(username=username, password=Password, email=collegeEmail,
                                                first_name=Firstname, last_name=Lastname)
        user.is_active = False
        user.save()
        request.session['institution_email'] = collegeEmail

        request.session['user'] = user.email
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={ 
                        'uidb64': uidb64, 'token': token_generator.make_token(user), 'new' : "new"})

        activate_url = 'https://' + domain + link

        message = render_to_string('mail_body.html', {
                                    'fname': Firstname, 'lname': Lastname, 'activate_url': activate_url})
        send_email(subject="You're just one step away...",
                            email=collegeEmail, message=message)
        send_email(subject="New Institution Added🎀",
                            email="sidharthv605@gmail.com", message=f"Name: {collegeName} \nEmail: {collegeEmail}")
        

        if Upload.objects.filter(email=username).exists():
            Upload.objects.filter(email=username).delete()

        if UnVerified.objects.filter(username=user.username).exists():
            UnVerified.objects.filter(username=user.username).delete()

        unverified = UnVerified(username=user.username, password=Password, email=username, firstname=Firstname, lastname=Lastname, gender=Gender, institution=collegeName, institution_email=collegeEmail, graduation_year=graduation_year, verification_url=activate_url)
        unverified.save()
        return redirect('/verification-message/')
            