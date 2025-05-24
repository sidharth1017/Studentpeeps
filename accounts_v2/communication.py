# communication.py
from django.conf import settings
from twilio.rest import Client

def send_otp_sms(phone: str, otp: str) -> bool:
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
