from typing import Literal
from ninja import Schema


class CheckoutRequestSchema(Schema):
    # SECURITY: item_id + item_type LANG ang tinatanggap dito. Walang
    # amount/price field — laging kukunin ang totoong presyo mula sa DB
    # (Product.price o Service.price), hinding-hindi mula sa client, para
    # maiwasan ang price tampering / URL manipulation.
    item_type: Literal['buy_and_sell', 'services']
    item_id: int


class CheckoutResponseSchema(Schema):
    checkout_url: str
    reference_number: str
    duplicate: bool = False


class TransactionListItemSchema(Schema):
    reference_number: str
    transaction_type: str
    status: str
    amount: float
    item_name: str | None = None
    checkout_url: str | None = None
    dispute_deadline: str | None = None
    released_at: str | None = None
    created_at: str
    updated_at: str


class ReleaseRequestSchema(Schema):
    reference_number: str


class ReleaseResponseSchema(Schema):
    reference_number: str
    status: str
    released_at: str
    transaction_type: str
    amount: float
    item_name: str | None = None
    buyer_username: str | None = None
    released_by_username: str | None = None