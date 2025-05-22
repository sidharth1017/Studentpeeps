from django.shortcuts import render
from ..models import *
from accounts_v2.models import *
from django.contrib import messages

def myaccount(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user

    if request.method == "POST":
        first_name = request.POST.get('fname')
        if first_name:
            profile.first_name = first_name
            profile.save()
            messages.success(request, "Profile updated successfully.")

    return render(request, 'edit_profile.html', {'profile': profile})
