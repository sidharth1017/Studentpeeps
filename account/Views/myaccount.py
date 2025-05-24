from django.shortcuts import render
from accounts_v2.models import *
from django.contrib import messages

def myaccount(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user
    userProfile = Register.objects.get(user__email=profile.email)

    if request.method == "POST":
        first_name = request.POST.get('fname')
        # phone = request.POST.get('phone')
        # email = request.POST.get('email')
        if first_name:
            profile.first_name = first_name
        # elif phone:
        #     userProfile.phone = phone
        # elif email:
        #     userProfile.user.email = email
        profile.save()
        messages.success(request, "Profile updated successfully.")

    return render(request, 'edit_profile.html', {'profile': userProfile})
