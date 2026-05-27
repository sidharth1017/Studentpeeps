from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from accounts_v2.models import Register

class PhoneBackend(BaseBackend):
    def authenticate(self, request, phone=None):
        try:
            register = Register.objects.get(phone=phone)
            return register.user
        except Register.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
