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

class AdminResolveDisputeSchema(Schema):
    decision: str
    admin_notes: str | None = None


class DisputeResponseSchema(Schema):
    id: int
    reference_number: str
    status: str
    admin_decision: str
    client_reason: str
    client_proof_image: str | None = None
    provider_counter_reason: str | None = None
    provider_proof_image: str | None = None
    response_deadline: str | None = None
    resolved_at: str | None = None
    resolved_by_username: str | None = None