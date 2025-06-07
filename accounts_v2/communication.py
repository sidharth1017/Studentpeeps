# communication.py
from django.conf import settings
from twilio.rest import Client
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.core.mail import EmailMessage
from utilities.models import Communication

def send_otp_sms_via_Twillio(phone: str, otp: str) -> bool:
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your Studentpeeps verification code is {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f"+91{phone}"
        )
        return True
    except Exception as e:
        print(f"Error sending OTP to {phone}: {e}")
        return False


def send_otp_sms_via_AWS_SNS(phone: str, otp: str) -> bool:
    try:
        client = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        message = f"Your Studentpeeps verification code is {otp}"
        phone_number = f"+91{phone}"

        client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        return True

    except (BotoCoreError, ClientError) as e:
        print(f"Error sending OTP to {phone}: {e}")
        return False

def send_otp(phone: str, otp: str) -> bool:
    try:
        sms_service = Communication.objects.get(channel='sms').service.lower().strip()
    except Communication.DoesNotExist:
        sms_service = 'sns'

    if sms_service == 'twilio':
        return send_otp_sms_via_Twillio(phone, otp)
    elif sms_service == 'sns':
        return send_otp_sms_via_AWS_SNS(phone, otp)
    else:
        print(f"Unsupported SMS service: {sms_service}")
        return send_otp_sms_via_AWS_SNS(phone, otp)


def send_welcome_email(subject, email, message):
    msg = EmailMessage(
                subject,
                message,
                f'Ayush from Studentpeeps <{settings.DEFAULT_FROM_EMAIL}>',
                [email],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send(fail_silently=False)
    return None

