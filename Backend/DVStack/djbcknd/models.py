from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. CORE & USER PROFILE MANAGEMENT
# ==========================================

class Profile(models.Model):
    """
    Para sa lahat ng user. Simple lang ang registration.
    Mabilis makakapag-post dito sa Buy & Sell tab nang walang hassle.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Pangunahing lungsod ng user")
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class ServiceProviderProfile(models.Model):
    """
    HIWALAY NA REQUIREMENTS PARA SA SERVICES LANG.
    Dito isusumite ang mga sensitibong dokumento. Admin lang ang makakakita nito sa backend.
    """
    APPROVAL_STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (Verified by ServiceMarket)'),
        ('REJECTED', 'Rejected'),
    )

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='service_profile')
    
    # --- SENSITIBONG IMPORMASYON (ADMIN ONLY) ---
    valid_id = models.ImageField(upload_to='providers/ids/', help_text="Admin lang ang makakatingin nito")
    detailed_address = models.TextField(help_text="Exact address para sa internal verification ni Admin")
    
    # --- LALABAS SA PUBLIC PROFILE ---
    provider_avatar = models.ImageField(upload_to='providers/avatars/', help_text="Profile picture na makikita sa Services Tab")
    
    # Ang status na babaguhin ni Admin sa Django Admin Panel pagkatapos suriin ang ID at Address
    approval_status = models.CharField(
        max_length=15, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='PENDING'
    )
    verified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Provider: {self.profile.user.username} - Status: {self.get_approval_status_display()}"


class Category(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('PRODUCT', 'Buy & Sell Tab'),
        ('SERVICE', 'Services Tab'),
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, default='PRODUCT')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"[{self.get_category_type_display()}] {self.name}"


# ==========================================
# 2. BUY & SELL TAB (Physical Goods)
# ==========================================

class Product(models.Model):
    PRODUCT_STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold Out'),
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products') 
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='products') # Diretso sa regular profile
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100, db_index=True) # City lang ang public
    status = models.CharField(max_length=15, choices=PRODUCT_STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


# ==========================================
# 3. SERVICES TAB (Labor, Repairs, Freelance)
# ==========================================

class Service(models.Model):
    SERVICE_STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('UNAVAILABLE', 'Unavailable/Full'),
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    
    # Naka-turo na sa ServiceProviderProfile na may mga requirements!
    provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE, related_name='services')
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    service_city = models.CharField(max_length=100, db_index=True) # Public location kung saan siya gumagawa
    status = models.CharField(max_length=15, choices=SERVICE_STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/')
    is_feature = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)