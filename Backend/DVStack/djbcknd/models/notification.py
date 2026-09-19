from django.contrib.auth.models import User
from django.db import models

from .service import Service, ServiceInquiry


class Notification(models.Model):
    """
    Notification model for alerting users about new messages and inquiries.
    """
    NOTIFICATION_TYPES = (
        ('MESSAGE', 'New Message'),
        ('INQUIRY', 'New Service Inquiry'),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='MESSAGE'
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    service_name = models.CharField(max_length=255, blank=True, null=True)

    # Optional: Link to related service or inquiry
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    inquiry = models.ForeignKey(
        ServiceInquiry,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    # Optional: Sender information
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"