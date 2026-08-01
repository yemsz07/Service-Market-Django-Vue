"""
Models configuration for djbcknd app.
Defines database tables and relationships for Users, Service Providers, Products, and Services.
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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


# ==========================================
# 🏷️ 2. CATEGORIES
# ==========================================

class Category(models.Model):
    """
    Categories used to classify both physical Products and bookable Services.
    """
    CATEGORY_TYPE_CHOICES = (
        ('PRODUCT', 'Buy & Sell Tab'),
        ('SERVICE', 'Services Tab'),
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(
        max_length=10, 
        choices=CATEGORY_TYPE_CHOICES, 
        default='PRODUCT'
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"[{self.get_category_type_display()}] {self.name}"


# ==========================================
# 🛒 3. BUY & SELL TAB (Physical Goods)
# ==========================================

class Product(models.Model):
    """
    Represents items for sale in the Buy & Sell marketplace.
    """
    PRODUCT_STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold Out'),
        ('RESERVED', 'Reserved'),
    )

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products'
    )
    seller = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100, db_index=True)
    status = models.CharField(
        max_length=15, 
        choices=PRODUCT_STATUS_CHOICES, 
        default='AVAILABLE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ProductImage(models.Model):
    """
    Stores image uploads attached to a Product.
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


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


# ==========================================
# 🔔 5. SIGNALS (Automatic Profile Generator)
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a matching Profile instance whenever a new User registers.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensures existing Profile updates cleanly when the User instance is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


# models.py (Idagdag sa pinakailalim)

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
        return f"Inquiry from {self.client.username} for {self.service.name}"


