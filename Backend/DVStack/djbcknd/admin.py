"""
Admin configuration for djbcknd app.
Customizes Django Admin Panel layouts, photo inline previews, verification fields, and filters.
"""

# ==========================================
# 📦 1. IMPORTS (Preparing our tools)
# ==========================================

from django.contrib import admin  # 🛠️ Django built-in Admin portal tools.
from django.utils.safestring import mark_safe  # 🛡️ Safety Tool: Allows raw HTML rendering for image preview tags.

from .models import (  # 🧸 Import database models to manage inside Admin.
    Category,
    Product,
    ProductImage,
    Profile,
    Service,
    ServiceImage,
    ServiceProviderProfile,
)

# ==========================================
# 🖼️ 2. INLINE MODELS (Embedded Multiple Photo Uploads)
# ==========================================

class ProductImageInline(admin.TabularInline):
    """
    Displays and manages gallery image uploads directly inside the main Product edit page.
    """
    model = ProductImage  # 🔗 Connects to ProductImage model.
    extra = 1  # ➕ Adds 1 empty image upload slot by default.
    readonly_fields = ['display_image']  # 🔒 Displays safe HTML photo preview in read-only mode.

    def display_image(self, obj):
        """
        Renders a small HTML thumbnail preview of the product image inside the inline table.
        """
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')  # 🖼️ HTML image tag.
        return "No Image"  # 🚫 Fallback text if no photo exists.
    display_image.short_description = "Preview"  # 🏷️ Column header title.


class ServiceImageInline(admin.TabularInline):
    """
    Displays and manages portfolio images directly inside the main Service edit page.
    """
    model = ServiceImage  # 🔗 Connects to ServiceImage model.
    extra = 1  # ➕ Adds 1 empty image upload slot by default.
    readonly_fields = ['display_image']  # 🔒 Displays safe HTML photo preview in read-only mode.

    def display_image(self, obj):
        """
        Renders a small HTML thumbnail preview of the service photo inside the inline table.
        """
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')  # 🖼️ HTML image tag.
        return "No Image"  # 🚫 Fallback text if no photo exists.
    display_image.short_description = "Preview"  # 🏷️ Column header title.


# ==========================================
# 🛡️ 3. MAIN ADMIN CUSTOMIZATIONS
# ==========================================

@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for verifying Service Providers.
    Allows Admins to inspect uploaded government IDs, addresses, avatars, and approve applicants.
    """
    list_display = ['get_username', 'approval_status', 'display_avatar_thumbnail', 'verified_at']  # 📋 Table columns in list view.
    list_filter = ['approval_status']  # 🔍 Sidebar filter by verification status (PENDING/APPROVED/REJECTED).
    search_fields = ['profile__user__username', 'detailed_address']  # 🔎 Search bar queries username or address.
    
    # 🔒 Image fields set to read-only so they cannot be accidentally overwritten while reviewing:
    readonly_fields = ['display_avatar', 'display_valid_id']
    
    # 📐 Groups edit form fields into clean section panels:
    fieldsets = [
        ('User Info', {'fields': ['profile', 'approval_status', 'verified_at']}),
        ('Sensitive Details (Admin Only)', {'fields': ['detailed_address', 'display_valid_id']}),
        ('Public Info', {'fields': ['display_avatar']}),
    ]

    # 🛠️ Helper Methods for Admin Views:
    def get_username(self, obj):
        """
        Fetches username from the linked User model.
        """
        return obj.profile.user.username
    get_username.short_description = 'Username'  # 🏷️ Column title.

    def display_avatar_thumbnail(self, obj):
        """
        Renders a tiny circular avatar thumbnail for list view table.
        """
        if obj.provider_avatar:
            return mark_safe(f'<img src="{obj.provider_avatar.url}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />')
        return "No Avatar"
    display_avatar_thumbnail.short_description = 'Avatar'  # 🏷️ Column title.

    def display_avatar(self, obj):
        """
        Renders a medium preview of the public avatar image inside detail view.
        """
        if obj.provider_avatar:
            return mark_safe(f'<img src="{obj.provider_avatar.url}" width="200" style="border-radius: 8px;" />')
        return "No Avatar uploaded"
    display_avatar.short_description = 'Provider Profile Picture'  # 🏷️ Section label.

    def display_valid_id(self, obj):
        """
        Renders a large preview of the uploaded Government ID for Admin verification.
        """
        if obj.valid_id:
            return mark_safe(f'<img src="{obj.valid_id.url}" width="400" style="border-radius: 8px; border: 1px solid #ccc;" />')
        return "No Valid ID uploaded"
    display_valid_id.short_description = 'Submitted Valid ID'  # 🏷️ Section label.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for managing Buy & Sell marketplace product listings.
    """
    list_display = ['name', 'seller', 'price', 'city', 'status', 'display_main_image', 'created_at']  # 📋 Table columns.
    list_filter = ['status', 'city', 'category']  # 🔍 Sidebar filters for fast navigation.
    search_fields = ['name', 'description', 'seller__user__username']  # 🔎 Search bar for items or sellers.
    list_editable = ['status']  # ⚡ Allows changing status (AVAILABLE -> SOLD) directly from table view.
    inlines = [ProductImageInline]  # 🖼️ Attaches multiple photo uploader at the bottom of the page.

    def display_main_image(self, obj):
        """
        Fetches featured image (or fallbacks to first photo) and displays a small square thumbnail.
        """
        main_img = obj.images.filter(is_feature=True).first() or obj.images.first()  # 🔍 Look for featured image.
        if main_img and main_img.image:
            return mark_safe(f'<img src="{main_img.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    display_main_image.short_description = 'Main Image'  # 🏷️ Column header.


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for managing Service marketplace listings.
    """
    list_display = ['name', 'provider', 'price', 'service_city', 'status', 'created_at']  # 📋 Table columns.
    list_filter = ['status', 'service_city', 'category']  # 🔍 Sidebar filters.
    search_fields = ['name', 'description', 'provider__profile__user__username']  # 🔎 Search bar for service titles or providers.
    list_editable = ['status']  # ⚡ Quick toggle availability directly from list view.
    inlines = [ServiceImageInline]  # 🖼️ Attaches multiple portfolio photo uploader.


# ==========================================
# 📌 4. SIMPLE MODEL REGISTRATIONS
# ==========================================

admin.site.register(Profile)  # 👤 Registers standard User Profile without extra customization.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin layout for managing Categories with auto-populating URL slugs.
    """
    prepopulated_fields = {'slug': ('name',)}  # ⚡ Auto-generates URL slug field as you type the category name!
    list_display = ['name', 'category_type']  # 📋 Table columns showing category title and tab type.