from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from accounts_v2.models import Register


def myaccount(request):
    if not request.user.is_authenticated:
        return redirect("IdentifyViewV2")

    profile = request.user
    from giftcard.models import Order

    try:
        filters = Q(user__email=profile.email)
        if len(profile.username) == 10:
            filters = Q(phone=profile.username)

        users = Register.objects.get(filters)
    except Register.DoesNotExist:
        try:
            baseUser = User.objects.get(username=profile.username)
        except User.DoesNotExist:
            baseUser = profile

        users = Register.objects.create(
            user=baseUser,
            firstname=baseUser.first_name,
            lastname=baseUser.last_name,
            is_verified=True,
        )

    if request.method == "POST":
        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        phone = request.POST.get("phone")
        birthday = request.POST.get("birthday")

        if first_name:
            users.firstname = first_name
        if phone:
            users.phone = phone
        if last_name:
            users.lastname = last_name
        if birthday:
            users.birthday = birthday

        users.save()
        messages.success(request, "Profile updated successfully.")

    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "pages/account/my_account.html",
        {
            "profile": users,
            "orders": orders,
        },
    )
