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
from django.contrib import messages
from typing import Tuple


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
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID_EMAIL,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_EMAIL,
            region_name=settings.AWS_REGION_EMAIL
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

        return response.status_code == 200 and "true" in response.text.lower()
    except Exception as e:
        print(f"Error sending OTP to {phone}: {e}")
        return False

def send_otp(request, phone: str, otp: str) -> Tuple[bool, bool]:
    today = now().date()

    otp_log, created = OTPSendLog.objects.get_or_create(phone=phone, date=today)

    if otp_log.count >= 5:
        messages.error(request, f"Rate limit exceeded for {phone}")
        print(f"Rate limit exceeded for {phone}")
        return False, True
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

    if success:
        with transaction.atomic():
            otp_log.count += 1
            otp_log.save()

    return success, False

def send_otp_email(email, otp, message):
    from_email = formataddr(('Studentpeeps', settings.DEFAULT_FROM_EMAIL))
    subject = f"{otp} is your Studentpeeps passcode."
    msg = EmailMessage(
                subject,
                message,
                from_email,
                [email],
            )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    return True


def send_welcome_email(subject, email, message):
    from_email = formataddr(('Studentpeeps', settings.DEFAULT_FROM_EMAIL))
    msg = EmailMessage(
                subject,
                message,
                from_email,
                [email],
            )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    return None

