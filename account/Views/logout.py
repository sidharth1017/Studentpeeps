from django.shortcuts import redirect
from django.contrib.auth.models import auth
from django.views.generic.base import View

class Logout(View):
    def get(self, request):
        auth.logout(request)
        return redirect('/')
        