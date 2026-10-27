from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task
def send_subscribe_email(subject, email, message):
    msg = EmailMessage(
        subject,
        message,
        f'Sanskriti from Studentpeeps <{settings.DEFAULT_FROM_EMAIL}>',
        [email],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    return None


@shared_task
def send_contact_mail(subject, name, email, message, emailList):
    body = f"""New Contact Us submission:
    Name: {name}
    Email: {email}
    Message: {message}"""

    msg = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        emailList,
    )
    msg.send(fail_silently=False)
    return None
