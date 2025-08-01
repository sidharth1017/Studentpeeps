from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth import login
from ..models import *

class IdUploadView(View):
    def get(self, request):
        return render(request, 'account/idcard_upload.html')

    def post(self, request):
        collegeIdProof = request.FILES['image']
        email = request.session.get('email')
        phone = request.session.get('phone')
        firstname = request.session.get('fname')
        lastname = request.session.get('lname')
        gender = request.session.get('gender')
        birthday = request.session.get('birthday')

        if collegeIdProof.size > 5 * 1024 * 1024:
            messages.error(request, 'File size exceeds 5MB.')
            return redirect('College-id-upload')
        
        user = None
        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
        elif User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        elif User.objects.filter(username=phone).exists():
            user = User.objects.get(username=phone)

        if user:
            if hasattr(user, 'is_active') and user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.info(request, "You are already a verified user.")
                return redirect('/')
            else:
                user.delete()


        user = User.objects.create_user(username=email or phone, email=email, first_name=firstname, last_name=lastname)
        user.is_active = False
        user.save()

        if UnVerified.objects.filter(email=email).exists():            
            UnVerified.objects.filter(email=email).delete()
        elif UnVerified.objects.filter(phone=phone).exists():            
            UnVerified.objects.filter(phone=phone).delete() 
        elif UnVerifiedIdUpload.objects.filter(user=user).exists():
            UnVerifiedIdUpload.objects.filter(user=user).delete()

        identifier = phone or email
        if AbandonedSignup.objects.filter(identifier=identifier).exists():
            AbandonedSignup.objects.filter(identifier=identifier).delete()        

        unVerifiedRegister = UnVerifiedIdUpload(user=user, phone=phone, firstname=firstname, lastname=lastname, gender=gender, birthday=birthday, collegeId=collegeIdProof)
        unVerifiedRegister.save()
        
        return redirect('/account/v2/student-verification-status')