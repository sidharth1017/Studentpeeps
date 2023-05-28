from celery import shared_task
from time import sleep
from django.core.mail import EmailMessage
from django.conf import settings


# Create your tasks here
@shared_task
def send_email(subject, email, message):
    msg = EmailMessage(
                subject,
                message,
                f'StudentPeeps <{settings.DEFAULT_FROM_EMAIL}>',
                [email],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send(fail_silently=False)
    return None


@shared_task
def send_welcome_email(subject, email, message):
    msg = EmailMessage(
                subject,
                message,
                f'Sanskriti from Studentpeeps <{settings.DEFAULT_FROM_EMAIL}>',
                [email],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send(fail_silently=False)
    return None

@shared_task
def send_subscribe_email(subject, email, message):
    msg = EmailMessage(
                subject,
                message,
                f'Sanskriti from Studentpeeps <{settings.DEFAULT_FROM_EMAIL}>',
                [email],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send(fail_silently=False)
    return None

@shared_task
def send_contact_mail(subject, name, email, message, emailList):
    msg = EmailMessage(
    subject,
    "Name: "+name+ ", Email: "+email+ ", Message: "+message,
    settings.DEFAULT_FROM_EMAIL,
    emailList,
    )
    msg.send(fail_silently=False)
    return None


@shared_task
def send_brand_mail(subject, name, email, brandname, brandsite, want, emailList):
    msg = EmailMessage(
    subject,
    "Name: "+name+ ", Email: "+email+ ", Brand Name: "+brandname+ ", Brand site: "+brandsite+ ", Why they want: "+want,
    settings.DEFAULT_FROM_EMAIL,
    emailList,
    )
    msg.send(fail_silently=False)
    return None


@shared_task
def send_course_mail(subject, name, collegename, email, linkedinurl, coursename, courselink, desc, emailList):
    msg = EmailMessage(
    subject,
    "Name: "+name+ ", Collegename: "+collegename+ ", Email: "+email+ ", Linkedin Url: "+ linkedinurl + ", Course Name: "+coursename+ ", Course link: "+courselink+ ", Why they want: "+desc,
    settings.DEFAULT_FROM_EMAIL,
    emailList,
    )
    msg.send(fail_silently=False)
    return None