from .services.checkout import get_or_create_transaction


def build_checkout_payload(
    item_name,
    description,
    amount_in_cents,
    success_url,
    cancel_url,
    reference_number,
    user_id,
    item_id,
    item_type,
):
    return {
        "data": {
            "attributes": {
                "send_email_receipt": True,
                "show_description": True,
                "show_line_items": True,
                "payment_method_types": ["card", "gcash", "paymaya", "dob"],
                "line_items": [
                    {
                        "currency": "PHP",
                        "amount": amount_in_cents,
                        "name": item_name,
                        "description": description,
                        "quantity": 1,
                    }
                ],
                "metadata": {
                    "reference_number": reference_number,
                    "transaction_type": item_type,
                    "user_id": str(user_id),
                    "item_id": str(item_id),
                },
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
        }
    }


def create_checkout(user, item_type, item_id, success_url, cancel_url):
    """
    Orchestration function: kinukuha/ginagawa muna yung atomic
    PaymentTransaction (price mula sa DB, may double-sale + double-pay
    guards), tapos binubuo ang payload papunta sa PayMongo.

    ASSUMPTION na kailangan mong i-verify: ginamit dito ang `.name` at
    `.description` fields ng Service model, katulad ng Product. Kung iba
    ang field names sa totoong Service model mo (hal. `title` sa halip
    ng `name`), sabihin mo lang para maitama.
    """
    txn, created = get_or_create_transaction(user, item_type, item_id)

    if not created and txn.paymongo_checkout_id:
        return txn, None

    amount_in_cents = int(txn.amount * 100)

    if item_type == 'buy_and_sell':
        item_name = txn.product.name
        description = txn.product.description
    else:
        item_name = txn.service.name          # <- i-verify: tamang field ba ito?
        description = txn.service.description  # <- i-verify: tamang field ba ito?

    payload = build_checkout_payload(
        item_name=item_name,
        description=description,
        amount_in_cents=amount_in_cents,
        success_url=success_url,
        cancel_url=cancel_url,
        reference_number=txn.reference_number,
        user_id=user.id,
        item_id=item_id,
        item_type=item_type,
    )

    return txn, payload
