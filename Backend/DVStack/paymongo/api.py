from typing import List

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from djbcknd.models import PaymentTransaction
from .schemas import (
    CheckoutRequestSchema, CheckoutResponseSchema,
    TransactionListItemSchema, ReleaseRequestSchema, ReleaseResponseSchema,
)
from .paymongo import create_checkout
from .services.checkout import ItemNotFoundError, ItemAlreadyPaidError, AmountExceedsLimitError
from .client import call_paymongo_checkout_session
from .security import CustomJWTAuth


router = Router(tags=["PayMongo Payments"], auth=CustomJWTAuth())


def _serialize_transaction(txn):
    item_name = None
    if txn.product_id:
        item_name = txn.product.name
    elif txn.service_id:
        item_name = txn.service.name  # i-verify: tamang field ba ito sa Service model mo?

    return {
        "reference_number": txn.reference_number,
        "transaction_type": txn.transaction_type,
        "status": txn.status,
        "amount": float(txn.amount),
        "item_name": item_name,
        "checkout_url": txn.checkout_url_cache,
        "dispute_deadline": txn.dispute_deadline.isoformat() if txn.dispute_deadline else None,
        "released_at": txn.released_at.isoformat() if txn.released_at else None,
        "created_at": txn.created_at.isoformat(),
        "updated_at": txn.updated_at.isoformat(),
    }


@router.post("/checkout/", response=CheckoutResponseSchema)
def create_checkout_endpoint(request, payload: CheckoutRequestSchema):
    current_user = request.user

    try:
        # Step 1: atomic, DB-only. Presyo mula sa DB, may double-sale +
        # double-pay guards. Walang HTTP call dito.
        txn, payload_dict = create_checkout(
            user=current_user,
            item_type=payload.item_type,
            item_id=payload.item_id,
            success_url=settings.PAYMONGO_SUCCESS_URL,
            cancel_url=settings.PAYMONGO_CANCEL_URL,
        )
    except ItemNotFoundError as exc:
        raise HttpError(404, str(exc))
    except ItemAlreadyPaidError as exc:
        raise HttpError(409, str(exc))
    except AmountExceedsLimitError as exc:
        raise HttpError(400, str(exc))

    # Step 2: duplicate request (parehong user, existing HOLD na may
    # checkout session na) -> ibalik ang cached URL, wag nang tumawag sa
    # PayMongo.
    if payload_dict is None:
        return {
            "checkout_url": txn.checkout_url_cache,
            "reference_number": txn.reference_number,
            "duplicate": True,
        }

    # Step 3: bagong transaction lang ito -> tumawag sa PayMongo API,
    # sa labas na ng row lock.
    status_code, response_data = call_paymongo_checkout_session(payload_dict)

    if status_code not in [200, 201]:
        error_detail = response_data.get("errors", [{}])[0].get(
            "detail", "Payment initialization failed."
        )
        raise HttpError(status_code if status_code >= 400 else 400, error_detail)

    checkout_url = response_data["data"]["attributes"]["checkout_url"]
    checkout_id = response_data["data"]["id"]

    # Step 4: hiwalay na save, pagkatapos ng successful response.
    txn.paymongo_checkout_id = checkout_id
    txn.checkout_url_cache = checkout_url
    txn.save(update_fields=["paymongo_checkout_id", "checkout_url_cache"])

    return {
        "checkout_url": checkout_url,
        "reference_number": txn.reference_number,
        "duplicate": False,
    }


@router.get("/transactions/", response=List[TransactionListItemSchema])
def list_all_transactions(request):
    """
    Ibinabalik ang LAHAT ng PayMongo transactions sa buong system
    (lahat ng users), pinaka-bagong-una. ADMIN-ONLY ito dahil sensitibong
    data (mga pangalan/presyo ng ibang users) — kailangan is_superuser=True
    ang naka-login na user.
    """
    if not request.user.is_superuser:
        raise HttpError(403, "Admin access lang ang puwede dito.")

    qs = (
        PaymentTransaction.objects
        .all()
        .select_related('user', 'product', 'service')
        .order_by('-created_at')
    )

    return [_serialize_transaction(txn) for txn in qs]


@router.post("/release/", response=ReleaseResponseSchema)
def release_payment(request, payload: ReleaseRequestSchema):
    """
    Manual na pag-release ng bayad papunta sa seller. ADMIN-ONLY.

    MAHALAGA: hindi ito naglilipat ng aktwal na pera — ang standard
    PayMongo checkout API mo ay walang built-in na per-transaction
    fund-routing papunta sa magkaibang seller. Ang ginagawa lang ng
    endpoint na ito ay markahan sa DB na "RELEASED" na ang desisyon
    (ibig sabihin, puwede nang i-payout ng admin ang halaga papunta sa
    seller nang manual, sa labas ng system na ito).
    """
    if not request.user.is_superuser:
        raise HttpError(403, "Admin access lang ang puwede dito.")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects
                .select_for_update()
                .select_related('user', 'product', 'service')
                .get(reference_number=payload.reference_number)
            )
        except PaymentTransaction.DoesNotExist:
            raise HttpError(404, "Walang natagpuang transaction sa reference number na ito.")

        if txn.status != 'PAID':
            raise HttpError(
                409,
                f"Hindi puwedeng i-release ang transaction na ito — kasalukuyang status: {txn.status}. "
                "PAID lang ang puwedeng i-release."
            )

        txn.status = 'RELEASED'
        txn.released_at = timezone.now()
        txn.released_by = request.user
        txn.save(update_fields=["status", "released_at", "released_by"])

    item_name = None
    if txn.product_id:
        item_name = txn.product.name
    elif txn.service_id:
        item_name = txn.service.name  # i-verify: tamang field ba ito sa Service model mo?

    return {
        "reference_number": txn.reference_number,
        "status": txn.status,
        "released_at": txn.released_at.isoformat(),
        "transaction_type": txn.transaction_type,
        "amount": float(txn.amount),
        "item_name": item_name,
        "buyer_username": txn.user.username,
        "released_by_username": txn.released_by.username if txn.released_by else None,
    }