import hashlib

from django.db import transaction, IntegrityError

from djbcknd.models import PaymentTransaction, Product, Service


class ItemNotFoundError(Exception):
    """Walang natagpuang Product/Service gamit ang ibinigay na item_id."""
    pass


class ItemAlreadyPaidError(Exception):
    """May existing PAID transaction na para sa item na ito (double-sale guard)."""
    pass


class AmountExceedsLimitError(Exception):
    """Lumagpas ang presyo sa OVERALL na max na tinatanggap ng PayMongo
    (kahit anong payment method), hindi na kayang iproseso kahit paano."""
    pass


# Overall na max ng PayMongo, kahit anong payment method — HARD LIMIT ito,
# walang paraan ang PayMongo na tumanggap ng amount na lampas dito.
# Overall na max ng PayMongo CHECKOUT SESSION (line item amount), kahit
# anong payment method — HARD LIMIT ito, kumpirmado mismo sa aktwal na
# error ng PayMongo API: "Amount can't be larger than 999,999.99."
# (Note: iba ito sa mas mataas na Payment Intent limit na ₱9,999,999.99 —
# mas mahigpit pala ang checkout session line item cap.)
PAYMONGO_ABSOLUTE_MAX_AMOUNT = 999_999.99

# GCash lang ang may mas mababang limitasyon kaysa sa ibang methods.
# HINDI natin dapat i-block ang buong checkout dahil dito — sa halip,
# aalisin na lang natin ang "gcash" sa listahan ng payment methods kung
# lumagpas dito, para gumana pa rin ang card/paymaya/atbp.
GCASH_MAX_AMOUNT = 100_000


def generate_idempotency_key(user_id, item_type, item_id, amount):
    """
    Deterministic hash base sa user+item_type+item_id+amount. Parehong
    request (double-click, double-submit) ay laging magbubunga ng
    parehong key.
    """
    raw = f"{user_id}:{item_type}:{item_id}:{amount}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _get_item_and_price(item_type, item_id):
    """
    THIS ONLY determines the price — NEVER from the client
    request. Get the item from the correct model based on item_type.
    """
    try:
        if item_type == 'buy_and_sell':
            item = Product.objects.get(id=item_id)
        elif item_type == 'services':
            item = Service.objects.get(id=item_id)
        else:
            raise ItemNotFoundError(f"Unknown item_type: {item_type}")
    except (Product.DoesNotExist, Service.DoesNotExist):
        raise ItemNotFoundError(f"No item found (type={item_type}, id={item_id}).")

    return item, item.price


@transaction.atomic
def get_or_create_transaction(user, item_type, item_id):
    """
    Generic version (buy_and_sell AND services) of atomic get-or-create.

    Protections here:

    1. PRICE TAMPERING GUARD — amount is always taken from DB
       (_get_item_and_price), NEVER from request payload.

    2. DOUBLE-SALE GUARD — if there's an existing PAID transaction for
       the same item (any user), raise ItemAlreadyPaidError.
       This only queries the PaymentTransaction table — no locking or
       touching the Product/Service model itself.

    3. DOUBLE-CLICK / DOUBLE-PAY GUARD (same user) — idempotency_key
       (user+item_type+item_id+amount) + select_for_update() on
       PaymentTransaction, plus DB-level partial UniqueConstraint as
       final safety net (IntegrityError fallback).

    Raises:
        ItemNotFoundError, ItemAlreadyPaidError
    """
    item, real_price = _get_item_and_price(item_type, item_id)

    if real_price > PAYMONGO_ABSOLUTE_MAX_AMOUNT:
        raise AmountExceedsLimitError(
            f"The price (₱{real_price:,.2f}) exceeds ₱{PAYMONGO_ABSOLUTE_MAX_AMOUNT:,.2f}, "
        "the maximum amount accepted by PayMongo regardless of the "
        "payment method. This cannot be processed."
        )

    # Double-sale guard: may nakabayad na ba dati para sa item na ito?
    filter_kwargs = (
        {'product_id': item_id} if item_type == 'buy_and_sell' else {'service_id': item_id}
    )
    already_paid = PaymentTransaction.objects.filter(
        status='PAID', **filter_kwargs
    ).exists()
    if already_paid:
        raise ItemAlreadyPaidError("May bayad na para sa item na ito.")

    idempotency_key = generate_idempotency_key(user.id, item_type, item_id, real_price)

    existing = (
        PaymentTransaction.objects
        .select_for_update()
        .filter(idempotency_key=idempotency_key, status='HOLD')
        .first()
    )
    if existing:
        return existing, False

    create_kwargs = dict(
        user=user,
        transaction_type='BUY_AND_SELL' if item_type == 'buy_and_sell' else 'SERVICES',
        amount=real_price,
        idempotency_key=idempotency_key,
        status='HOLD',
    )
    if item_type == 'buy_and_sell':
        create_kwargs['product'] = item
    else:
        create_kwargs['service'] = item

    try:
        txn = PaymentTransaction.objects.create(**create_kwargs)
        return txn, True
    except IntegrityError:
        return PaymentTransaction.objects.get(
            idempotency_key=idempotency_key, status='HOLD'
        ), False