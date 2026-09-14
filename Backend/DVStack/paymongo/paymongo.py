import base64
import requests
from django.conf import settings

class PayMongoService:
    BASE_URL = "https://api.paymongo.com/v1"

    def __init__(self):
        # Reads the secret key from settings.py
        secret_key = getattr(settings, 'PAYMONGO_SECRET_KEY', '')
        
        # PayMongo requires Basic Auth using a Base64-encoded Secret Key
        encoded_key = base64.b64encode(f"{secret_key}:".encode('utf-8')).decode('utf-8')
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_key}"
        }

    def create_checkout_session(self, amount, description, success_url, cancel_url):
        url = f"{self.BASE_URL}/checkout_sessions"
        
        # PayMongo uses centavos (e.g., 500 PHP = 50000 centavos)
        amount_in_centavos = int(float(amount) * 100)

        payload = {
            "data": {
                "attributes": {
                    "send_email_receipt": True,
                    "show_description": True,
                    "show_line_items": True,
                    "payment_method_types": ["card", "gcash", "paymaya", "dob"],
                    "line_items": [
                        {
                            "currency": "PHP",
                            "amount": amount_in_centavos,
                            "description": description,
                            "name": description,
                            "quantity": 1
                        }
                    ],
                    "success_url": success_url,
                    "cancel_url": cancel_url
                }
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            return 500, {"errors": [{"detail": f"Network error: {str(e)}"}]}