from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# ==========================================
# 👤 1. USER PROFILE & PROVIDER MANAGEMENT
# ==========================================

class Profile(models.Model):
    """
    Standard profile created automatically for every registered user.
    Used for basic marketplace features like posting products in the Buy & Sell tab.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Main city location of user"
    )
    contact_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class ServiceProviderProfile(models.Model):
    """
    Separate requirements specifically for offering Services.
    Stores sensitive verification documents visible only to Admins.
    """
    APPROVAL_STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (Verified by ServiceMarket)'),
        ('REJECTED', 'Rejected'),
    )

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='service_profile'
    )

    # 🔒 Sensitive Verification Information (Admin Only)
    valid_id = models.ImageField(
        upload_to='providers/ids/',
        help_text="Government ID photo for admin verification only"
    )
    detailed_address = models.TextField(
        help_text="Exact home address for internal verification"
    )

    # 🌐 Public Information
    provider_avatar = models.ImageField(
        upload_to='providers/avatars/',
        help_text="Profile picture shown on Services Tab"
    )

    # 🛡️ Admin Verification & Audit Fields
    approval_status = models.CharField(
        max_length=15,
        choices=APPROVAL_STATUS_CHOICES,
        default='PENDING'
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when approved by Admin"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for admin review (e.g., 'ID verified', 'Blurry photo')."
    )

    def save(self, *args, **kwargs):
        """
        Auto-sets the verified_at timestamp when status is set to APPROVED,
        or resets it if the status changes back or gets rejected.
        """
        if self.approval_status == 'APPROVED' and self.verified_at is None:
            self.verified_at = timezone.now()
        elif self.approval_status != 'APPROVED':
            self.verified_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Provider: {self.profile.user.username} - Status: {self.get_approval_status_display()}"