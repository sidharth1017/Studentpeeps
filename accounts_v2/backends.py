from django.contrib.auth.backends import BaseBackend
from accounts_v2.models import Register

class PhoneBackend(BaseBackend):
    def authenticate(self, request, phone=None):
        try:
            return Register.objects.get(phone=phone)
        except Register.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Register.objects.get(pk=user_id)
        except Register.DoesNotExist:
            return None
