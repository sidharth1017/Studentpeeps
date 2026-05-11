import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from django.conf import settings
from django.utils import timezone
from giftcard.models import Provider
from giftcard.providers.woohoo.token_manager import WoohooTokenManager
from giftcard.providers.woohoo.signature import WoohooSignature

def generate_woohoo_status_curl():
    provider = Provider.objects.get(id="woohoo")
    token_manager = WoohooTokenManager(provider)
    
    # Target reference id from the user's prompt
    refno = "34a39532-a33c-47e1-90fe-796775617ef3" 
    
    # 1. Get fresh token
    token = token_manager.get_token()
    date_at_client = timezone.now().isoformat()
    
    # 2. Define endpoint mapping for Order Status
    # URL Format: /rest/v3/orders/{refno}/status 
    url = f"{settings.WOOHOO_BASE_URL}/rest/v3/orders/{refno}/status"
    method = "GET"
    
    # 3. Generate precise HMAC signature (assuming NO body for GET)
    signature = WoohooSignature.generate(
        method=method,
        url=url,
        query=None,
        body=None,
        secret=settings.WOOHOO_CLIENT_SECRET
    )
    
    # 4. Build curl string
    curl_command = f"""curl -X GET "{url}" \\
     -H "Authorization: Bearer {token}" \\
     -H "Content-Type: application/json" \\
     -H "dateAtClient: {date_at_client}" \\
     -H "signature: {signature}" """
     
    print("\n\n" + "="*80)
    print("READY TO USE CURL COMMAND (Valid for a few minutes):")
    print("="*80 + "\n")
    print(curl_command)
    print("\n" + "="*80)

if __name__ == "__main__":
    generate_woohoo_status_curl()
