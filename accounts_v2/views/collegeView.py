from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.urls import reverse
from account.utils import token_generator
from account.tasks import send_email
from ..models import *
from django.contrib import messages

class CollegeView(View):
    def post(self, request):
        collegeName = request.POST['institution_name']
        collegeEmail = request.POST['institution_email']
        graduation_year = request.POST['graduation_year']        

        email = request.session.get('email') 
        phone = request.session.get('phone') 
        firstName = request.session.get('fname')
        lastName = request.session.get('lname')
        gender = request.session.get('gender')
        birthday = request.session.get('birthday')


        user = None
        if User.objects.filter(username=collegeEmail).exists():
            user = User.objects.get(username=collegeEmail)
        elif User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
        elif User.objects.filter(email=collegeEmail).exists():
            user = User.objects.get(email=collegeEmail)

        if user:
            if hasattr(user, 'is_active') and user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.info(request, "You are already a verified user.")
                return redirect('/')
            else:
                user.delete()


        if (phone):
            user = User.objects.create_user(username=collegeEmail, email=collegeEmail, first_name=firstName, last_name=lastName)
            user.is_active = False
            user.save()
        else:
            user = User.objects.create_user(username=email, email=collegeEmail, first_name=firstName, last_name=lastName)
            user.is_active = False
            user.save()

        request.session['user'] = user.email
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={ 
                        'uidb64': uidb64, 'token': token_generator.make_token(user), 'new' : "new"})
        activate_url = 'https://' + domain + link


        if UnVerified.objects.filter(institution_email=collegeEmail).exists():
            UnVerified.objects.filter(institution_email=collegeEmail).delete()

        unverified = UnVerified(user=user, email=email, phone=phone, firstname=firstName, lastname=lastName, gender=gender, birthday=birthday, institution=collegeName, institution_email=collegeEmail, graduation_year=graduation_year, verification_url=activate_url)
        unverified.save()

        try:
            message = render_to_string('emailers/verify_institution_email_body.html', {
                                       'fname': firstName, 'lname': lastName, 'activate_url': activate_url})
            send_email(subject="Verify your Studentpeeps account",
                             email=[collegeEmail], message=message)
                             
        except Exception as e:
            print(f"Email sending failed: {e}")
        

        return redirect('/verification-message/')
            