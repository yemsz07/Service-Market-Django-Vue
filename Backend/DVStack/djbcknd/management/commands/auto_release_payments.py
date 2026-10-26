from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djbcknd.models import PaymentTransaction

from paymongo.notifications import notify_payment_released


class Command(BaseCommand):
    help = (
        "Automatically release PAID transactions that have passed "
        "their dispute_deadline (no dispute filed). Should "
        "be run repeatedly using cron job or Celery beat "
        "(for example, once per hour)."
    )

    def handle(self, *args, **options):
        now = timezone.now()

        # Get only PAID transactions past deadline
        eligible = (
            PaymentTransaction.objects
            .filter(status='PAID', dispute_deadline__lte=now)
            .values_list('id', flat=True)
        )

        released_count = 0
        for txn_id in eligible:
            with transaction.atomic():

                # select_for_update + re-check status: to prevent
                # double-release if this command runs simultaneously
                # with the manual release endpoint.
                txn = (
                    PaymentTransaction.objects
                    .select_for_update()
                    .get(id=txn_id)
                )
                if txn.status != 'PAID':
                    continue  # maybe already released or disputed while
                              # command is currently running

                txn.status = 'RELEASED'
                txn.released_at = now
                txn.released_by = None  # None = auto-release, no admin
                txn.save(update_fields=["status", "released_at", "released_by"])
                released_count += 1

                self.stdout.write(
                    f"  Released: {txn.reference_number} (₱{txn.amount})"
                )

                notify_payment_released(txn)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {released_count} transaction(s) auto-released."
            )
        )
