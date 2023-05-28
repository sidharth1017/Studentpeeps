from django.shortcuts import render
from ..models import *

def myaccount(request):
    users = request.user.email
    if Registers.objects.filter(institution_email=users).exists() or Registers.objects.filter(email=users).exists():
        if Registers.objects.filter(institution_email=users).exists():
            profile = Registers.objects.get(institution_email=users)
        else:
            profile = Registers.objects.get(email=users)
        if request.method == "POST":
            FirstName = request.POST['fname']
            LastName = request.POST['lname']
            Gender = request.POST['Gender']
            # Date = request.POST['date']
            # Month = request.POST['month']
            # Year = request.POST['year']
            images = request.FILES['image']
            profile.firstname = FirstName
            profile.lastname = LastName
            profile.gender = Gender
            # profile.date = Date
            # profile.month = Month
            # profile.year = Year
            profile.profile_image = images
            profile.save()
        return render(request, 'edit_profile.html', {'profile': profile})
    else:
        profile = Upload.objects.get(email=users)
        if request.method == "POST":
            FirstName = request.POST['fname']
            LastName = request.POST['lname']
            Gender = request.POST['Gender']
            # Date = request.POST['date']
            # Month = request.POST['month']
            # Year = request.POST['year']
            images = request.FILES['image']
            profile.firstname = FirstName
            profile.lastname = LastName
            profile.gender = Gender
            # profile.date = Date
            # profile.month = Month
            # profile.year = Year
            profile.profile_image = images
            profile.save()
        return render(request, 'edit_profile.html', {'profile': profile})
