# Idagdag ito sa djbcknd/admin.py mo (o gawing bagong import kung
# hiwalay na file ang gusto mo) — huwag palitan ang buong admin.py,
# idagdag lang ang mga ito.

from django.contrib import admin
from django.utils import timezone
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "transaction_type",
        "user",
        "amount",
        "status",
        "dispute_deadline",
        "released_at",
        "released_by",
        "created_at",
    )
    list_filter = ("status", "transaction_type")
    search_fields = ("reference_number", "user__username", "paymongo_checkout_id")
    readonly_fields = (
        "reference_number", "idempotency_key", "checkout_url_cache",
        "paymongo_checkout_id", "created_at", "updated_at",
    )
    ordering = ("-created_at",)

    actions = ["release_selected_payments"]

    @admin.action(description="Release selected PAID payments to the seller/Service Provider")
    def release_selected_payments(self, request, queryset):
        """
        Admin action: pinipili ni admin ang mga row sa listahan, tapos
        i-click ang action na ito — parehong logic ng POST /release/
        endpoint, pero diretso sa loob ng Django Admin.
        """
        eligible = queryset.filter(status="PAID")
        skipped_count = queryset.exclude(status="PAID").count()

        released_count = 0
        for txn in eligible:
            txn.status = "RELEASED"
            txn.released_at = timezone.now()
            txn.released_by = request.user
            txn.save(update_fields=["status", "released_at", "released_by"])
            released_count += 1

        if released_count:
            self.message_user(request, f"{released_count} transaction(s) na-release.")
        if skipped_count:
            self.message_user(
                request,
                f"{skipped_count} transaction(s) ang na-skip (hindi PAID ang status).",
                level="warning",
            )
