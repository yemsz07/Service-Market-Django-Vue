"""
Models configuration for djbcknd app.
Defines database tables and relationships for Users, Service Providers, Products, and Services.
"""

# ==========================================
# 📦 1. IMPORTS (Preparing our tools)
# ==========================================

from django.contrib.auth.models import User  # 👤 Default Django User model.
from django.db import models  # 🗄️ Django ORM tool to build database tables.
from django.db.models.signals import post_save  # 🔔 Event Listener: Triggers actions after a model is saved.
from django.dispatch import receiver  # 📑 Receiver decorator to handle signals.


# ==========================================
# 👤 2. CORE & USER PROFILE MANAGEMENT
# ==========================================

class Profile(models.Model):
    """
    Standard profile created automatically for every registered user.
    Used for basic marketplace features like posting products in the Buy & Sell tab.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 🔗 Connects 1-to-1 with a Django User. Deletes if user is deleted.
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Main city location of user")  # 🏙️ User's city location.
    contact_number = models.CharField(max_length=15, blank=True, null=True)  # 📞 Phone/Mobile number.
    created_at = models.DateTimeField(auto_now_add=True)  # ⏰ Timestamp when profile was created.

    def __str__(self):
        return self.user.username  # 🗣️ Displays username in Django Admin.


class ServiceProviderProfile(models.Model):
    """
    Separate requirements specifically for offering Services.
    Stores sensitive verification documents visible only to Admins.
    """
    APPROVAL_STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (Verified by ServiceMarket)'),
        ('REJECTED', 'Rejected'),
    )  # 🚦 Verification statuses.

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='service_profile')  # 🔗 Links directly to standard Profile.
    
    # 🔒 SENSITIVE INFORMATION (ADMIN ONLY):
    valid_id = models.ImageField(upload_to='providers/ids/', help_text="Government ID photo for admin verification only")  # 🪪 ID upload.
    detailed_address = models.TextField(help_text="Exact home address for internal verification")  # 🏠 Private full address.
    
    # 🌐 PUBLIC INFORMATION:
    provider_avatar = models.ImageField(upload_to='providers/avatars/', help_text="Profile picture shown on Services Tab")  # 🖼️ Public avatar photo.
    
    # 🛡️ Admin Verification Field:
    approval_status = models.CharField(
        max_length=15, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='PENDING'
    )  # 🚦 Approval status managed by Admin.
    verified_at = models.DateTimeField(blank=True, null=True)  # ⏰ Date & time when approved by Admin.

    def __str__(self):
        return f"Provider: {self.profile.user.username} - Status: {self.get_approval_status_display()}"  # 🗣️ Admin display string.


class Category(models.Model):
    """
    Categories used to classify both physical Products and bookable Services.
    """
    CATEGORY_TYPE_CHOICES = (
        ('PRODUCT', 'Buy & Sell Tab'),
        ('SERVICE', 'Services Tab'),
    )  # 🏷️ Tab placement choices.

    name = models.CharField(max_length=100)  # 🔤 Category title (e.g., "Electronics" or "Plumbing").
    slug = models.SlugField(unique=True)  # 🔗 URL-friendly version of the name.
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, default='PRODUCT')  # 📌 Identifies tab type.

    class Meta:
        verbose_name_plural = "Categories"  # ✏️ Fixes plural spelling in Django Admin ("Categories" instead of "Categorys").

    def __str__(self):
        return f"[{self.get_category_type_display()}] {self.name}"  # 🗣️ Displays type and name in Admin.


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
    )  # 🚦 Item availability statuses.

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')  # 🏷️ Optional link to Category.
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='products')  # 👤 Links directly to normal seller Profile.
    name = models.CharField(max_length=200)  # 🔤 Product title.
    description = models.TextField()  # 📝 Full item description.
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 💵 Price format (e.g., 1500.00).
    city = models.CharField(max_length=100, db_index=True)  # 🏙️ Indexed city location for faster query search.
    status = models.CharField(max_length=15, choices=PRODUCT_STATUS_CHOICES, default='AVAILABLE')  # 🚦 Listing status.
    created_at = models.DateTimeField(auto_now_add=True)  # ⏰ Date listed.
    updated_at = models.DateTimeField(auto_now=True)  # ⏰ Date last modified.

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"  # 🗣️ Displays item name and status.


class ProductImage(models.Model):
    """
    Stores image uploads attached to a Product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')  # 🔗 Links to parent Product.
    image = models.ImageField(upload_to='products/')  # 🖼️ Upload destination folder for product photos.
    is_feature = models.BooleanField(default=False)  # ⭐️ Flags if image is the primary cover photo.
    uploaded_at = models.DateTimeField(auto_now_add=True)  # ⏰ Upload timestamp.


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
    )  # 🚦 Service availability statuses.

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')  # 🏷️ Optional link to Category.
    provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE, related_name='services')  # 👷 Links to verified Provider Profile!
    
    name = models.CharField(max_length=200)  # 🔤 Service title (e.g., "Aircon Cleaning").
    description = models.TextField()  # 📝 Details about what the service includes.
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 💵 Service rate/fee.
    service_city = models.CharField(max_length=100, db_index=True)  # 🏙️ Location where the service is offered.
    status = models.CharField(max_length=15, choices=SERVICE_STATUS_CHOICES, default='AVAILABLE')  # 🚦 Availability status.
    created_at = models.DateTimeField(auto_now_add=True)  # ⏰ Listing timestamp.
    updated_at = models.DateTimeField(auto_now=True)  # ⏰ Last edit timestamp.

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"  # 🗣️ Displays service title and status.


class ServiceImage(models.Model):
    """
    Stores gallery image uploads attached to a Service listing.
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')  # 🔗 Links to parent Service.
    image = models.ImageField(upload_to='services/')  # 🖼️ Upload destination folder for service photos.
    is_feature = models.BooleanField(default=False)  # ⭐️ Flags if image is featured cover photo.
    uploaded_at = models.DateTimeField(auto_now_add=True)  # ⏰ Upload timestamp.


# ==========================================
# 🔔 5. SIGNALS (Automatic Profile Generator)
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a matching Profile instance whenever a new User registers.
    """
    if created:
        Profile.objects.create(user=instance)  # ⚡ Auto-creates base Profile for new user.


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensures existing Profile updates cleanly when the User instance is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()  # 💾 Safely updates linked Profile without throwing errors if profile exists.