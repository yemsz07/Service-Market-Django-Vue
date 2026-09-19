from django.contrib.auth.models import User
from django.db import models

from .category import Category
from .profile import ServiceProviderProfile


# ==========================================
# 🛠️ 4. SERVICES TAB (Labor & Repairs)
# ==========================================

class Service(models.Model):
    """
    Represents services offered by verified Service Providers.
    """
    SERVICE_STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('UNAVAILABLE', 'Unavailable/Full'),
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    provider = models.ForeignKey(
        ServiceProviderProfile,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service_city = models.CharField(max_length=100, db_index=True)
    status = models.CharField(
        max_length=15,
        choices=SERVICE_STATUS_CHOICES,
        default='AVAILABLE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ServiceImage(models.Model):
    """
    Stores gallery image uploads attached to a Service listing.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='services/')
    is_feature = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ServiceInquiry(models.Model):
    INQUIRY_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RESPONDED', 'Responded'),
    )

    # Sino ang nagtanong (Client / Customer)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_inquiries'
    )

    # Anong serbisyo ang itinatanong
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )

    # Ang mismong mensahe ng client
    message = models.TextField()

    # Status ng inquiry (Pending o Responded)
    status = models.CharField(
        max_length=15,
        choices=INQUIRY_STATUS_CHOICES,
        default='PENDING'
    )

    # Petsa kung kailan naipadala (Date Received sa table)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.service.name}"