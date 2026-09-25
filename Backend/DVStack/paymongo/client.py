import base64

import requests
from django.conf import settings

PAYMONGO_CHECKOUT_SESSIONS_URL = "https://api.paymongo.com/v1/checkout_sessions"


def _get_auth_header():
    """
    PayMongo uses HTTP Basic Auth kung saan yung secret key ang username,
    walang password. Kailangan i-base64-encode yung "secret_key:" string.
    """
    encoded = base64.b64encode(f"{settings.PAYMONGO_SECRET_KEY}:".encode()).decode()
    return f"Basic {encoded}"


def call_paymongo_checkout_session(payload_dict):
    """
    Nagpapadala ng aktwal na HTTP request papunta sa PayMongo API para
    gumawa ng checkout session. Tumatanggap ng payload_dict na galing sa
    build_buy_and_sell_payload().

    Returns:
        (status_code, response_data)
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": _get_auth_header(),
    }

    response = requests.post(
        PAYMONGO_CHECKOUT_SESSIONS_URL,
        json=payload_dict,
        headers=headers,
        timeout=15,
    )

    return response.status_code, response.json()
