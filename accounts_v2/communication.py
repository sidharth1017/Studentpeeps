# communication.py
from django.conf import settings
from twilio.rest import Client
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.core.mail import EmailMessage
from utilities.models import Communication, OTPSendLog
from django.utils.timezone import now
from django.db import transaction
from email.utils import formataddr
import requests


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

def send_otp_sms_via_fast2sms(phone: str, otp: str) -> bool:
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"

        payload = {
            'authorization': settings.FAST2SMS_ACCESS_KEY_ID,
            'sender_id': 'SDNT',
            'message': '189200',
            'variables_values': f"{otp}|{otp}",
            'route': 'dlt',
            'numbers': phone,
        }

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.get(url, params=payload, headers=headers)

        print("Fast2SMS response:", response.text)

        return response.status_code == 200 and "true" in response.text.lower()
    except Exception as e:
        print(f"Error sending OTP to {phone}: {e}")
        return False

def send_otp(phone: str, otp: str) -> bool:
    today = now().date()

    # Check if an OTP record exists for today
    otp_log, created = OTPSendLog.objects.get_or_create(phone=phone, date=today)

    if otp_log.count >= 2:
        print(f"Rate limit exceeded for {phone}")
        return False

    # Get SMS service
    try:
        sms_service = Communication.objects.get(channel='sms').service.lower().strip()
    except Communication.DoesNotExist:
        sms_service = 'sns'

    # Send SMS
    if sms_service == 'twilio':
        success = send_otp_sms_via_Twillio(phone, otp)
    elif sms_service == 'sns':
        success = send_otp_sms_via_AWS_SNS(phone, otp)
    elif sms_service == 'fast2sms':
        success = send_otp_sms_via_fast2sms(phone, otp)
    else:
        print(f"Unsupported SMS service: {sms_service}")
        success = send_otp_sms_via_fast2sms(phone, otp)

    # Update count if sent successfully
    if success:
        with transaction.atomic():
            otp_log.count += 1
            otp_log.save()

    return success


def send_welcome_email(subject, email, message):
    from_email = formataddr(('Ayush from Studentpeeps', settings.DEFAULT_FROM_EMAIL))
    msg = EmailMessage(
                subject,
                message,
                from_email,
                [email],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send(fail_silently=False)
    return None

