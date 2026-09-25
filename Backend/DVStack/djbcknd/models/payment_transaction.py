import uuid
from django.db import models
from django.conf import settings


class PaymentTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY_AND_SELL', 'Buy and Sell'),
        ('SERVICES', 'Services'),
    )

    STATUS_CHOICES = (
    ('HOLD', 'Hold / Pending Payment'),
    ('PAID', 'Paid / Held in Escrow'),       
    ('RELEASED', 'Released to Seller/Service Provider'),       
    ('CANCELLED', 'Cancelled'),
    ('DISPUTED', 'Under Dispute'),
    ('REFUNDED', 'Refunded'),
)

    DISPUTE_DECISION_CHOICES = (
        ('PENDING', 'Pending Admin Review'),
        ('FAVOR_CLIENT', 'Favor to Client (Refund)'),
        ('FAVOR_PROVIDER', 'Favor to Provider/Seller (Release Payment)'),
    )

    # ==========================================
    # CORE TRANSACTION FIELDS
    # ==========================================
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Unique internal reference number for reconciliation and PayMongo metadata"
    )

    # NEW: deterministic hash (user+product/service+amount) used to detect
    # duplicate checkout requests caused by double-clicks / double submits.
    # This is DIFFERENT from reference_number, which is random on purpose.
    idempotency_key = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text="Deterministic hash (user+product+amount) used to detect duplicate checkout requests"
    )

    # NEW: cache of the PayMongo checkout_url so duplicate requests can be
    # answered without calling the PayMongo API again.
    checkout_url_cache = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Cached PayMongo checkout_url, returned again on duplicate requests"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_transactions",
        help_text="The user who checked out or paid"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    # Optional / Flexible Mapping para sa Buy & Sell o Services
    product = models.ForeignKey(
        'djbcknd.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions",
        help_text="Link for Buy & Sell product (null if Services transaction)"
    )
    service = models.ForeignKey(
        'djbcknd.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions",
        help_text="Link for Service booking (null if Buy & Sell transaction)"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Exact amount of peso (e.g., 2500.00)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='HOLD')
    paymongo_checkout_id = models.CharField(max_length=250, null=True, blank=True, db_index=True)

    released_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Kailan i-release ang bayad papunta sa seller (manual o auto)"
    )
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="released_transactions",
        help_text="Admin na nag-release ng bayad (null kung auto-release)"
    )

    # ==========================================
    # CANCELLATION & TWO-SIDED DISPUTE SYSTEM
    # ==========================================
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_cancellations",
        help_text="User or Provider who initiated the cancellation/dispute"
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Side 1: Client / Buyer Side
    client_reason = models.TextField(null=True, blank=True, help_text="Complaint or reason of Client/Buyer")
    client_proof_image = models.ImageField(upload_to="cancellation_proofs/client/", null=True, blank=True)

    # Side 2: Service Provider / Seller Side (Karapatan mag-counter)
    provider_counter_reason = models.TextField(null=True, blank=True, help_text="Appeal of Provider/Seller")
    provider_proof_image = models.ImageField(upload_to="cancellation_proofs/provider/", null=True, blank=True)

    # SLA Timer & Auto-Resolution
    dispute_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Response Window (5-7 days) for response of both users"
    )
    auto_resolved = models.BooleanField(
        default=False,
        help_text="Flag the background task resolved the dispute because no response"
    )

    # Admin Resolution / Tagahatol
    admin_decision = models.CharField(
        max_length=20,
        choices=DISPUTE_DECISION_CHOICES,
        default='PENDING',
        help_text="Final decision of Admin who will receive the funds"
    )
    admin_notes = models.TextField(null=True, blank=True, help_text="Reason or explanation of Admin's decision")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        constraints = [
            # NEW: prevents more than one HOLD buy-and-sell transaction for
            # the same user+product at the same time (race-condition guard
            # at the database level — this is Postgres-only, uses a partial
            # unique index).
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(status='HOLD', transaction_type='BUY_AND_SELL'),
                name='unique_hold_buy_and_sell_per_user_product'
            ),
            # NEW: same idea, for SERVICES transactions.
            models.UniqueConstraint(
                fields=['user', 'service'],
                condition=models.Q(status='HOLD', transaction_type='SERVICES'),
                name='unique_hold_service_per_user_service'
            ),
        ]

    def __str__(self):
        return f"{self.reference_number} | {self.transaction_type} | {self.status}"

    def save(self, *args, **kwargs):
        # Auto-generate ng Reference Number bago i-save sa DB
        if not self.reference_number:
            prefix = "REF-BS" if self.transaction_type == 'BUY_AND_SELL' else "REF-SRV"
            self.reference_number = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
