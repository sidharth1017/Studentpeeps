from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import View
from ..tasks import send_email

class UploadEmail(View):
    def get(self, request):
        return render(request, 'uploademail.html')

    def post(self, request):
        messages = None
        email = request.POST['email']
        message = render_to_string('mail_body_upload.html')
        send_email(subject="Welcome to the club + your 🔑", email=email, message=message)
        messages = "Mail Sent!!"
        return render(request, 'uploademail.html', {'message': messages})
