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
    """Lumagpas ang presyo sa max na tinatanggap ng piniling payment methods."""
    pass


# GCash (isa sa mga payment_method_types natin) ay may sariling mas
# mababang limitasyon kaysa sa overall na ₱9,999,999.99 ng PayMongo.
# Kailangan i-validate ito DITO, bago pa man tumawag sa PayMongo API,
# para hindi na kailangang mag-fail sa gitna ng checkout.
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
    ITO LANG ang pinagmumulan ng presyo — hinding-hindi mula sa client
    request. Kunin ang item mula sa tamang model base sa item_type.
    """
    try:
        if item_type == 'buy_and_sell':
            item = Product.objects.get(id=item_id)
        elif item_type == 'services':
            item = Service.objects.get(id=item_id)
        else:
            raise ItemNotFoundError(f"Hindi kilalang item_type: {item_type}")
    except (Product.DoesNotExist, Service.DoesNotExist):
        raise ItemNotFoundError(f"Walang natagpuang item (type={item_type}, id={item_id}).")

    return item, item.price


@transaction.atomic
def get_or_create_transaction(user, item_type, item_id):
    """
    Generic na bersyon (buy_and_sell AT services) ng atomic get-or-create.

    Mga proteksyon dito:

    1. PRICE TAMPERING GUARD — ang amount ay laging kinukuha mula sa DB
       (_get_item_and_price), hinding-hindi mula sa request payload.

    2. DOUBLE-SALE GUARD — kung may existing PAID transaction na para sa
       parehong item (kahit sinong user), itataas ang ItemAlreadyPaidError.
       Query lang ito sa PaymentTransaction table — walang ginagalaw o
       kinukuha na lock sa Product/Service model mismo.

    3. DOUBLE-CLICK / DOUBLE-PAY GUARD (parehong user) — idempotency_key
       (user+item_type+item_id+amount) + select_for_update() sa
       PaymentTransaction, plus DB-level partial UniqueConstraint bilang
       huling safety net (IntegrityError fallback).

    Raises:
        ItemNotFoundError, ItemAlreadyPaidError
    """
    item, real_price = _get_item_and_price(item_type, item_id)

    if real_price > GCASH_MAX_AMOUNT:
        raise AmountExceedsLimitError(
            f"Ang presyo (₱{real_price:,.2f}) ay lumalagpas sa ₱{GCASH_MAX_AMOUNT:,.2f} "
            "na limitasyon para sa GCash. Piliin ang ibang payment method (card, atbp.) "
            "o kontakin ang PayMongo para sa mas mataas na limitasyon."
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