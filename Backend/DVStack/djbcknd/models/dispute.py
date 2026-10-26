from django.db import models
from django.conf import settings


class Dispute(models.Model):

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("PROVIDER_RESPONDED", "Provider Responded"),
        ("RESOLVED", "Resolved"),
    )

    DECISION_CHOICES = (
        ("PENDING", "Pending Admin Review"),
        ("FAVOR_CLIENT", "Favor Client"),
        ("FAVOR_PROVIDER", "Favor Provider"),
    )

    payment_transaction = models.OneToOneField(
        "djbcknd.PaymentTransaction",
        on_delete=models.CASCADE,
        related_name="dispute",
    )

    filed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="filed_disputes",
    )
    filed_at = models.DateTimeField(auto_now_add=True)

    client_reason = models.TextField()
    client_proof_image = models.ImageField(upload_to="disputes/client/")

    provider_counter_reason = models.TextField(null=True, blank=True)
    provider_proof_image = models.ImageField(
        upload_to="disputes/provider/", null=True, blank=True
    )
    provider_responded_at = models.DateTimeField(null=True, blank=True)

    response_deadline = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="OPEN")

    admin_decision = models.CharField(
        max_length=30, choices=DECISION_CHOICES, default="PENDING"
    )
    admin_notes = models.TextField(null=True, blank=True)

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="resolved_disputes",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    auto_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dispute #{self.id} | {self.payment_transaction.reference_number} | {self.status}"
