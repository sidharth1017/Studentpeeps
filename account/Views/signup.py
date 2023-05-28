from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.base import View
from ..models import *
from ..utils import token_generator
from ..tasks import send_email
from validate_email import validate_email


class SignUp(View):
    def get(self, request):
        colleges = College.objects.order_by('name')
        Institution = {college.name: college.emails for college in colleges}
        return render(request, 'signup3.html', {'Institution': Institution})

    def post(self, request):
        colleges = College.objects.order_by('name')
        Institution = {college.name: college.emails for college in colleges}
        institution = request.POST['institution']
        collegeEmail = request.POST['institution_email']
        graduation_year = request.POST['graduation_year']

        request.session['institution_name'] = institution
        request.session['institution_email'] = collegeEmail
        request.session['graduation_year'] = graduation_year

        domains = Institution.get(institution)
        if domains is None:
            messages.error(
                request, "Ohh! Looks like your college email doesn't match with your institution database. If you think it's a mistake, please shoot us a mail at verify@studentpeeps.club")
            return render(request, 'signup3.html', {'Institution': Institution})
        afterSlice = collegeEmail.split("@")
        sliceValue = afterSlice[1]
        i = 0
        for i in domains:
            dom = i
            if(dom == sliceValue):
                domains = sliceValue
                break

        if Registers.objects.filter(institution_email=collegeEmail).exists():
            messages.error(request, 'Institution email is already Taken')
            return redirect('signup')

        if(sliceValue == domains):
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
                           'uidb64': uidb64, 'token': token_generator.make_token(user), 'new' : 'exist'})

            activate_url = 'https://' + domain + link

            message = render_to_string('mail_body.html', {
                                       'fname': Firstname, 'lname': Lastname, 'activate_url': activate_url})
            send_email(subject="You’re just one step away+ gift 🔒",
                             email=collegeEmail, message=message)

            if Upload.objects.filter(email=username).exists():
                Upload.objects.filter(email=username).delete()

            if UnVerified.objects.filter(username=user.username).exists():
                UnVerified.objects.filter(username=user.username).delete()

            unverified = UnVerified(username=user.username, password=Password, email=username, firstname=Firstname, lastname=Lastname, gender=Gender, institution=institution, institution_email=collegeEmail, graduation_year=graduation_year, verification_url=activate_url)
            unverified.save()
            return redirect('/verification-message/')
        else:
            messages.error(
                request, "Ohh! Looks like your college email doesn't match with your institution database. If you think it's a mistake, please shoot us a mail at verify@studentpeeps.club")
            return render(request, 'signup3.html', {'Institution': Institution})
            
        
class TestEmail(View):
    def get(self, request, *args, **kwargs):
        # email1 = "ashishpatil96579@gmail.com"
        # is_valid1 = validate_email(email1)
        
        # email2 = "Sidharthverma@jklu.edu.in"
        # is_valid2 = validate_email(email2)
        return HttpResponse(f"Done!")
        