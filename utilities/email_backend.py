import json
import urllib.request
import urllib.error
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMultiAlternatives

class ZeptoMailAPIBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        # Using the SMTP password as the API Send Mail Token
        self.api_token = kwargs.get('api_token') or getattr(settings, 'ZEPTO_SMTP', {}).get('PASSWORD')
        host = getattr(settings, 'ZEPTO_SMTP', {}).get('HOST', 'smtp.zeptomail.in')
        
        # Infer API URL from SMTP host (e.g. smtp.zeptomail.in -> api.zeptomail.in)
        api_host = host.replace('smtp.', 'api.')
        self.api_url = f"https://{api_host}/v1.1/email"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
            
        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, message):
        if not self.api_token:
            if not self.fail_silently:
                raise ValueError("ZeptoMail API Token is not configured.")
            return False

        auth_header = self.api_token
        if not auth_header.startswith("Zoho-enczapikey"):
            auth_header = f"Zoho-enczapikey {self.api_token}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        # Parse recipients
        to_address = [{"email_address": {"address": addr}} for addr in message.to]
        cc_address = [{"email_address": {"address": addr}} for addr in message.cc] if message.cc else []
        bcc_address = [{"email_address": {"address": addr}} for addr in message.bcc] if message.bcc else []

        # Parse sender
        from_email_raw = message.from_email or settings.DEFAULT_FROM_EMAIL
        import email.utils
        from_name, from_addr = email.utils.parseaddr(from_email_raw)
        
        payload = {
            "from": {"address": from_addr or from_email_raw},
            "to": to_address,
            "subject": message.subject,
        }
        
        if from_name:
            payload["from"]["name"] = from_name
            
        if cc_address:
            payload["cc"] = cc_address
        if bcc_address:
            payload["bcc"] = bcc_address

        # Check for HTML content
        is_html = False
        if isinstance(message, EmailMultiAlternatives):
            for content, mimetype in message.alternatives:
                if mimetype == "text/html":
                    payload["htmlbody"] = content
                    is_html = True
                    break
                    
        # If it's HTML but not multi-alternative (or if no html was found)
        if message.content_subtype == "html":
            payload["htmlbody"] = message.body
        elif not is_html:
            payload["textbody"] = message.body

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in (200, 201):
                    return True
        except urllib.error.URLError as e:
            if not self.fail_silently:
                raise e
        
        return False
