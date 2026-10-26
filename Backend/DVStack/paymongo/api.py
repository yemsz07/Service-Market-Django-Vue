from typing import List

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from djbcknd.models import PaymentTransaction, Dispute


from ninja import Form, File
from ninja.files import UploadedFile
from .schemas import (
    CheckoutRequestSchema, CheckoutResponseSchema,
    TransactionListItemSchema, ReleaseRequestSchema, ReleaseResponseSchema,
    AdminResolveDisputeSchema, DisputeResponseSchema,
)
from .services.dispute import (
    file_dispute, respond_to_dispute, resolve_dispute,
    DisputeError, DisputePermissionError, InvalidDisputeStateError,
    DisputeDeadlineError, get_provider_user,
)


from .paymongo import create_checkout
from .services.checkout import ItemNotFoundError, ItemAlreadyPaidError, AmountExceedsLimitError
from .client import call_paymongo_checkout_session
from .security import CustomJWTAuth
from .notifications import notify_payment_released
from django.db.models import Q




router = Router(tags=["PayMongo Payments"], auth=CustomJWTAuth())


def _serialize_transaction(txn):
    item_name = None
    if txn.product_id:
        item_name = txn.product.name
    elif txn.service_id:
        item_name = txn.service.name  # verify: is this the correct field in your Service model?

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
    Returns ALL PayMongo transactions in the entire system
    (all users), newest first. ADMIN-ONLY because of sensitive
    data (other users' names/prices) — requires is_superuser=True
    for the logged-in user.
    """
    if not request.user.is_superuser:
        raise HttpError(403, "Admin access only allowed here.")

    qs = (
        PaymentTransaction.objects
        .all()
        .select_related('user', 'product', 'service')
        .order_by('-created_at')
    )

    return [_serialize_transaction(txn) for txn in qs]


@router.get("/my-payments/", response=List[TransactionListItemSchema])
def list_my_transactions(request):
    """
    Returns the logged-in user's transactions only (for My Payments page).
    """
    qs = (
        PaymentTransaction.objects
        .filter(user=request.user)
        .select_related('product', 'service')
        .order_by('-created_at')
    )

    return [_serialize_transaction(txn) for txn in qs]


@router.post("/release/", response=ReleaseResponseSchema)
def release_payment(request, payload: ReleaseRequestSchema):
    """
    Manual payment release to seller. ADMIN-ONLY.

    IMPORTANT: This does not transfer actual money — the standard
    PayMongo checkout API has no built-in per-transaction
    fund-routing to different sellers. This endpoint only marks
    the DB as "RELEASED" (meaning admin can manually payout
    the amount to the seller outside this system).
    """
    if not request.user.is_superuser:
        raise HttpError(403, "Admin access only allowed here.")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects
                .select_for_update()
                .select_related('user', 'product', 'service')
                .get(reference_number=payload.reference_number)
            )
        except PaymentTransaction.DoesNotExist:
            raise HttpError(404, "No transaction found with that reference number.")

        if txn.status != 'PAID':
            raise HttpError(
                409,
                f"Cannot release this transaction — current status: {txn.status}. "
                "Only PAID transactions can be released."
            )

        txn.status = 'RELEASED'
        txn.released_at = timezone.now()
        txn.released_by = request.user
        txn.save(update_fields=["status", "released_at", "released_by"])

        notify_payment_released(txn)

    item_name = None
    if txn.product_id:
        item_name = txn.product.name
    elif txn.service_id:
        item_name = txn.service.name  # verify: is this the correct field in your Service model?

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


def _serialize_dispute(dispute):
    return {
        "id": dispute.id,
        "reference_number": dispute.payment_transaction.reference_number,
        "status": dispute.status,
        "admin_decision": dispute.admin_decision,
        "client_reason": dispute.client_reason,
        "client_proof_image": dispute.client_proof_image.url if dispute.client_proof_image else None,
        "provider_counter_reason": dispute.provider_counter_reason,
        "provider_proof_image": dispute.provider_proof_image.url if dispute.provider_proof_image else None,
        "response_deadline": dispute.response_deadline.isoformat() if dispute.response_deadline else None,
        "resolved_at": dispute.resolved_at.isoformat() if dispute.resolved_at else None,
        "resolved_by_username": dispute.resolved_by.username if dispute.resolved_by else None,
    }


# ============================================================
# 1. CLIENT/BUYER FILES DISPUTE — may REQUIRED na proof image
# ============================================================
@router.post("/disputes/{reference_number}/file/", response=DisputeResponseSchema)
def file_dispute_endpoint(
    request,
    reference_number: str,
    client_reason: str = Form(...),
    client_proof_image: UploadedFile = File(...),
):
    try:
        dispute = file_dispute(
            user=request.user,
            reference_number=reference_number,
            client_reason=client_reason,
            client_proof_image=client_proof_image,
        )
    except DisputePermissionError as exc:
        raise HttpError(403, str(exc))
    except InvalidDisputeStateError as exc:
        raise HttpError(409, str(exc))
    except DisputeError as exc:
        raise HttpError(400, str(exc))

    return _serialize_dispute(dispute)


# ============================================================
# 2. SELLER/PROVIDER RESPONDS — may REQUIRED na proof image
# ============================================================
@router.post("/disputes/{reference_number}/respond/", response=DisputeResponseSchema)
def respond_dispute_endpoint(
    request,
    reference_number: str,
    provider_counter_reason: str = Form(...),
    provider_proof_image: UploadedFile = File(...),
):
    try:
        dispute = respond_to_dispute(
            user=request.user,
            reference_number=reference_number,
            provider_counter_reason=provider_counter_reason,
            provider_proof_image=provider_proof_image,
        )
    except DisputePermissionError as exc:
        raise HttpError(403, str(exc))
    except DisputeDeadlineError as exc:
        raise HttpError(409, str(exc))
    except InvalidDisputeStateError as exc:
        raise HttpError(409, str(exc))
    except DisputeError as exc:
        raise HttpError(400, str(exc))

    return _serialize_dispute(dispute)


# ============================================================
# 3. GET DISPUTE DETAILS —
# ============================================================
@router.get("/disputes/{reference_number}/", response=DisputeResponseSchema)
def get_dispute_details(request, reference_number: str):
    try:
        txn = (
            PaymentTransaction.objects
            .select_related("user", "product", "service", "dispute")
            .get(reference_number=reference_number)
        )
    except PaymentTransaction.DoesNotExist:
        raise HttpError(404, "Payment transaction not found.")

    try:
        dispute = txn.dispute
    except Dispute.DoesNotExist:
        raise HttpError(404, "No dispute exists for this transaction.")

    current_user = request.user
    is_client = txn.user_id == current_user.id
    provider = get_provider_user(txn)
    is_provider = provider is not None and provider.id == current_user.id
    is_admin = current_user.is_superuser

    if not (is_client or is_provider or is_admin):
        raise HttpError(403, "You do not have permission to view this dispute.")

    return _serialize_dispute(dispute)


# ============================================================
# 4. ADMIN RESOLUTION
# ============================================================
@router.post("/disputes/{reference_number}/resolve/", response=DisputeResponseSchema)
def resolve_dispute_endpoint(request, reference_number: str, payload: AdminResolveDisputeSchema):
    try:
        dispute, txn = resolve_dispute(
            admin_user=request.user,
            reference_number=reference_number,
            decision=payload.decision,
            admin_notes=payload.admin_notes,
        )
    except DisputePermissionError as exc:
        raise HttpError(403, str(exc))
    except InvalidDisputeStateError as exc:
        raise HttpError(409, str(exc))
    except DisputeError as exc:
        raise HttpError(400, str(exc))

    return _serialize_dispute(dispute)


@router.get("/my-earnings/", response=List[TransactionListItemSchema])
def list_my_released_payments(request):
    """
    Ibinabalik ang mga RELEASED na transactions kung saan ang naka-login
    na user ay ang seller/provider (hindi admin-only ito, dahil sariling
    kita lang ng user ang ipinapakita).
    """
    current_user = request.user
    qs = (
        PaymentTransaction.objects
        .filter(
            status='RELEASED'   
        )
        .filter(
            Q(product__seller__user=current_user) |
            Q(service__provider__profile__user=current_user)
        )
        .select_related('user', 'product', 'service')
        .order_by('-released_at')
    )
    return [_serialize_transaction(txn) for txn in qs]