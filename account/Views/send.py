from ..models import UnVerified
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.views.generic.base import View
from django.urls import reverse
from ..utils import token_generator
from ..tasks import send_email

class Send(View):
    def get(self, request):
        unverifiedUsers = UnVerified.objects.all()
        for unverifiedUser in unverifiedUsers:
            user = User.objects.get(email=unverifiedUser.institution_email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={
                            'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'https://' + domain + link
            message = render_to_string('mail_body.html', {
                                        'fname': user.first_name, 'lname': user.last_name, 'activate_url': activate_url})
            send_email(subject="you're just one step away...", email=user.email, message=message)
            return HttpResponse('Mail Send!!')
        return HttpResponse('Mail Not Send!!')
