import hashlib
import hmac
import json

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from ninja import Router

from djbcknd.models import PaymentTransaction

# WALANG CustomJWTAuth dito — si PayMongo mismo ang tumatawag sa
# endpoint na ito, hindi ang logged-in na user. Sa halip,
# pinoprotektahan natin ito gamit ang signature verification (HMAC).
webhook_router = Router(tags=["PayMongo Webhook"])

# Ilang araw bago awtomatikong ma-release ang bayad kung walang dispute
HOLD_PERIOD_DAYS = 5


def _verify_signature(raw_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False

    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
    except ValueError:
        return False

    timestamp = parts.get("t")
    provided_signature = parts.get("li") or parts.get("te")
    if not timestamp or not provided_signature:
        return False

    signed_payload = f"{timestamp}.{raw_body.decode()}"
    expected_signature = hmac.new(
        settings.PAYMONGO_WEBHOOK_SECRET.encode(),
        signed_payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, provided_signature)


@webhook_router.post("/webhook/")
def paymongo_webhook(request):
    raw_body = request.body
    signature_header = request.headers.get("Paymongo-Signature", "")

    if not _verify_signature(raw_body, signature_header):
        return HttpResponse(status=400)

    event = json.loads(raw_body)
    attributes = event.get("data", {}).get("attributes", {})
    event_type = attributes.get("type")
    event_data = attributes.get("data", {})

    if event_type == "checkout_session.payment.paid":
        checkout_id = event_data.get("id")
        if checkout_id:
            _mark_paid(checkout_id)

    elif event_type == "payment.failed":
        checkout_id = event_data.get("attributes", {}).get("checkout_session_id")
        if checkout_id:
            _mark_failed(checkout_id)

    return HttpResponse(status=200)


@transaction.atomic
def _mark_paid(checkout_id):
    try:
        txn = (
            PaymentTransaction.objects
            .select_for_update()
            .get(paymongo_checkout_id=checkout_id)
        )
    except PaymentTransaction.DoesNotExist:
        return

    # IDEMPOTENT: puwedeng ma-deliver nang paulit-ulit ng PayMongo ang
    # parehong webhook event (retries). Kung PAID na o lampas na, huwag
    # na ulitin.
    if txn.status != 'HOLD':
        return

    txn.status = 'PAID'
    # I-set ang deadline: kung walang dispute na na-file sa loob ng
    # HOLD_PERIOD_DAYS, awtomatikong mare-release (via management command).
    txn.dispute_deadline = timezone.now() + timedelta(days=HOLD_PERIOD_DAYS)
    txn.save(update_fields=["status", "dispute_deadline"])

    # TODO: dito mo idadagdag ang pag-send ng automatic system message
    # sa chat window (buyer + seller) na nagsasabing "Paid na ang item.
    # Ire-release ang bayad sa seller sa loob ng 5 araw kung walang dispute."


@transaction.atomic
def _mark_failed(checkout_id):
    try:
        txn = (
            PaymentTransaction.objects
            .select_for_update()
            .get(paymongo_checkout_id=checkout_id)
        )
    except PaymentTransaction.DoesNotExist:
        return

    if txn.status != 'HOLD':
        return

    txn.status = 'CANCELLED'
    txn.save(update_fields=["status"])
