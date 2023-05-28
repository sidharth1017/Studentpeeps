from ..models import UnVerified, Registers
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.base import View
from ..tasks import send_email

class SendMailToUnverifieds(View):
    def get(self, request):
        # users = Registers.objects.order_by("firstname")[100:500]
        users = "mittalayush740@gmail.com"

        
        for unverifiedUser in users:
            message = render_to_string('mail_body_event.html')
            send_email(subject="Tech Talks at 5 PM 🔥", email= "mittalayush740@gmail.com", message=message)
            return HttpResponse('Mail Send!! sss')
        return HttpResponse('Mail Not Send!!')