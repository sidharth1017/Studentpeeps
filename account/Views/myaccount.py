from django.shortcuts import render
from accounts_v2.models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from accounts_v2.models import Register

def myaccount(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user
    users = Register.objects.get(Q(phone=profile.username) | Q(user__email=profile.email))

    if request.method == "POST":
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone = request.POST.get('phone')

        if first_name:
            users.first_name = first_name
        if phone:
            users.phone = phone
        if last_name:
            users.user.lastname = last_name

        users.save()
        messages.success(request, "Profile updated successfully.")

    return render(request, 'edit_profile.html', {'profile': users})
