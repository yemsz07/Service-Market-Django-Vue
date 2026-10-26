from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from djbcknd.models import PaymentTransaction, Dispute




DISPUTE_RESPONSE_DAYS = 5

DISPUTE_OPEN = "OPEN"
DISPUTE_PROVIDER_RESPONDED = "PROVIDER_RESPONDED"
DISPUTE_RESOLVED = "RESOLVED"

PAID = "PAID"
DISPUTED = "DISPUTED"
REFUNDED = "REFUNDED"
RELEASED = "RELEASED"

FAVOR_CLIENT = "FAVOR_CLIENT"
FAVOR_PROVIDER = "FAVOR_PROVIDER"

MAX_REASON_LENGTH = 2000
MAX_ADMIN_NOTES_LENGTH = 5000
MAX_PROOF_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class DisputeError(Exception):
    pass


class DisputePermissionError(DisputeError):
    pass


class InvalidDisputeStateError(DisputeError):
    pass


class DisputeDeadlineError(DisputeError):
    pass


def validate_reason(value, field_name="reason", max_length=MAX_REASON_LENGTH):
    if value is None:
        raise DisputeError(f"{field_name} is required.")

    value = value.strip()
    if not value:
        raise DisputeError(f"{field_name} cannot be empty.")

    if len(value) > max_length:
        raise DisputeError(f"{field_name} cannot exceed {max_length} characters.")

    return value


def validate_proof_image(image, field_name="Proof image"):
    """
    REQUIRED proof image — must be validated before saving.
    Gets the size and content type, rejects if over limit or not allowed image type.
    """
    if not image:
        raise DisputeError(f"{field_name} is required.")

    if image.size > MAX_PROOF_SIZE:
        raise DisputeError(f"{field_name} is too large. Maximum size is 5 MB.")

    content_type = getattr(image, "content_type", None)
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise DisputeError(f"{field_name} must be a JPEG, PNG, or WebP image.")


def get_provider_user(txn):
    """
    Returns the actual User object of the seller/provider of a
    transaction — CONSISTENT User object always, for correct
    comparison in .id in respond_to_dispute().

    CONFIRMED that the following chains (based on your actual
    Profile/Service models):

      Product.seller -> Profile -> Profile.user -> User

      Service.provider -> ServiceProviderProfile -> .profile
                        -> Profile -> Profile.user -> User

    (Two levels in Service path — ServiceProviderProfile is
    a separate model with its own .profile FK back to Profile.)
    """
    if txn.product_id:
        seller_profile = getattr(txn.product, "seller", None)  # Profile
        if seller_profile is None:
            return None
        return getattr(seller_profile, "user", None)

    if txn.service_id:
        service_provider_profile = getattr(txn.service, "provider", None)  # ServiceProviderProfile
        if service_provider_profile is None:
            return None
        profile = getattr(service_provider_profile, "profile", None)  # Profile
        if profile is None:
            return None
        return getattr(profile, "user", None)  # User

    return None


def file_dispute(*, user, reference_number, client_reason, client_proof_image):
    """
    Client/buyer creates a dispute. PAID -> DISPUTED.
    REQUIRED ang client_proof_image.
    """
    client_reason = validate_reason(client_reason, "Client reason")
    validate_proof_image(client_proof_image, "Client proof image")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects
                .select_for_update()
                .select_related("product", "service", "service__provider")
                .get(reference_number=reference_number)
            )
        except PaymentTransaction.DoesNotExist:
            raise DisputeError("Payment transaction not found.")

        if txn.user_id != user.id:
            raise DisputePermissionError("You are not the client of this transaction.")

        if txn.status != PAID:
            raise InvalidDisputeStateError(
                f"Transaction must be PAID. Current status: {txn.status}"
            )

        # Belt-and-suspenders: OneToOneField na rin ang nagbabawal nito
        # sa DB level, pero mas malinaw ang error message kung dito
        # natin muna ito huhulihin.
        if Dispute.objects.filter(payment_transaction=txn).exists():
            raise InvalidDisputeStateError("A dispute already exists for this transaction.")

        now = timezone.now()

        dispute = Dispute.objects.create(
            payment_transaction=txn,
            filed_by=user,
            client_reason=client_reason,
            client_proof_image=client_proof_image,
            response_deadline=now + timedelta(days=DISPUTE_RESPONSE_DAYS),
            status=DISPUTE_OPEN,
            admin_decision="PENDING",
        )

        txn.status = DISPUTED
        txn.save(update_fields=["status", "updated_at"])

        return dispute


def respond_to_dispute(*, user, reference_number, provider_counter_reason, provider_proof_image):
    """
    Seller/provider responds to an open dispute. OPEN -> PROVIDER_RESPONDED.
    REQUIRED ang provider_proof_image.
    """
    provider_counter_reason = validate_reason(provider_counter_reason, "Provider counter reason")
    validate_proof_image(provider_proof_image, "Provider proof image")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects
                .select_for_update()
                .select_related("product", "service", "service__provider")
                .get(reference_number=reference_number)
            )
        except PaymentTransaction.DoesNotExist:
            raise DisputeError("Payment transaction not found.")

        if txn.status != DISPUTED:
            raise InvalidDisputeStateError("Transaction is not currently under dispute.")

        try:
            dispute = txn.dispute
        except Dispute.DoesNotExist:
            raise DisputeError("Dispute record does not exist.")

        if dispute.status != DISPUTE_OPEN:
            raise InvalidDisputeStateError("Provider response has already been submitted.")

        provider = get_provider_user(txn)
        if provider is None:
            raise DisputeError("Unable to determine seller/provider.")

        if provider.id != user.id:
            raise DisputePermissionError("You are not the seller/provider of this transaction.")

        now = timezone.now()

        if dispute.response_deadline and now > dispute.response_deadline:
            raise DisputeDeadlineError("The provider response deadline has expired.")

        dispute.provider_counter_reason = provider_counter_reason
        dispute.provider_proof_image = provider_proof_image
        dispute.provider_responded_at = now
        dispute.status = DISPUTE_PROVIDER_RESPONDED

        dispute.save(update_fields=[
            "provider_counter_reason", "provider_proof_image",
            "provider_responded_at", "status", "updated_at",
        ])

        return dispute


def resolve_dispute(*, admin_user, reference_number, decision, admin_notes=None):
    """
    Admin resolves the dispute. DISPUTED -> REFUNDED (favor client)
    or DISPUTED -> RELEASED (favor provider).

    ADMIN-ONLY: is_superuser only, not is_staff (deliberately strict,
    based on your decision about this sensitive access).

    Can be called even if dispute.status is still OPEN (provider
    hasn't responded yet) — for example, if deadline passed and
    admin wants to resolve immediately without waiting for
    a meaningless counter-response.
    """
    from paymongo.notifications import notify_payment_released
    if not admin_user.is_superuser:
        raise DisputePermissionError("Admin access required.")

    if decision not in (FAVOR_CLIENT, FAVOR_PROVIDER):
        raise DisputeError("Invalid dispute decision.")

    if admin_notes:
        admin_notes = admin_notes.strip()
        if len(admin_notes) > MAX_ADMIN_NOTES_LENGTH:
            raise DisputeError(f"Admin notes cannot exceed {MAX_ADMIN_NOTES_LENGTH} characters.")

    with transaction.atomic():
        try:
            txn = (
                PaymentTransaction.objects
                .select_for_update()
                .get(reference_number=reference_number)
            )
        except PaymentTransaction.DoesNotExist:
            raise DisputeError("Payment transaction not found.")

        if txn.status != DISPUTED:
            raise InvalidDisputeStateError(
                f"Transaction is not DISPUTED. Current status: {txn.status}"
            )

        try:
            dispute = txn.dispute
        except Dispute.DoesNotExist:
            raise DisputeError("Dispute record does not exist.")

        if dispute.status == DISPUTE_RESOLVED:
            raise InvalidDisputeStateError("This dispute has already been resolved.")

        if dispute.admin_decision != "PENDING":
            raise InvalidDisputeStateError("This dispute already has an admin decision.")

        now = timezone.now()

        dispute.admin_decision = decision
        dispute.admin_notes = admin_notes
        dispute.resolved_by = admin_user
        dispute.resolved_at = now
        dispute.status = DISPUTE_RESOLVED

        dispute.save(update_fields=[
            "admin_decision", "admin_notes", "resolved_by", "resolved_at",
            "status", "updated_at",
        ])

        # PROTOTYPE PAYMENT STATE — hindi ito aktwal na tumatawag sa
        # PayMongo para sa refund o payout, internal state lang ito.
        if decision == FAVOR_CLIENT:
            txn.status = REFUNDED
        elif decision == FAVOR_PROVIDER:
            txn.status = RELEASED
            txn.released_at = now
            txn.released_by = admin_user

        txn.save(update_fields=["status", "released_at", "released_by", "updated_at"])

        return dispute, txn
