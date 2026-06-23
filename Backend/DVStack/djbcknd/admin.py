from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, ServiceProviderProfile, Category, Product, ProductImage, Service, ServiceImage

# ==========================================
# INLINE MODELS: Para sa 1-to-Many Relationships
# ==========================================

class ProductImageInline(admin.TabularInline):
    """
    Nagbibigay ng interface sa loob ng Product admin page para 
    mag-upload ng maraming larawan nang sabay-sabay.
    """
    model = ProductImage
    extra = 1 # Bilang ng blangkong form fields na lalabas
    readonly_fields = ['display_image']

    def display_image(self, obj):
        # Preview function para makita ang image sa Admin panel
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')
        return "No Image"
    display_image.short_description = "Image Preview"


class ServiceImageInline(admin.TabularInline):
    """
    Katulad ng ProductImageInline, pero para sa Service portfolio.
    """
    model = ServiceImage
    extra = 1
    readonly_fields = ['display_image']

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')
        return "No Image"
    display_image.short_description = "Image Preview"


# ==========================================
# MAIN ADMIN CONFIGURATIONS
# ==========================================

@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    """
    Admin portal para sa Service Provider verification process.
    Focus nito ay ang mabilis na validation ng IDs at Avatars.
    """
    # Columns na makikita sa list view
    list_display = ['get_username', 'approval_status', 'display_avatar_thumbnail', 'verified_at']
    # Sidebar filters para mabilis ma-sort ang mga pending applications
    list_filter = ['approval_status']
    # Search bar configuration
    search_fields = ['profile__user__username', 'detailed_address']
    
    # Ginagawang readonly ang mga sensitive files sa edit page para sa security
    readonly_fields = ['display_avatar', 'display_valid_id']
    
    # Pag-aayos ng layout ng form para sa mas magandang user interface
    fieldsets = [
        ('User Info', {'fields': ['profile', 'approval_status', 'verified_at']}),
        ('Sensitibong Detalye (Admin Only)', {'fields': ['detailed_address', 'display_valid_id']}),
        ('Public Info', {'fields': ['display_avatar']}),
    ]

    # Helper methods para sa pag-format ng admin table display
    def get_username(self, obj):
        return obj.profile.user.username
    get_username.short_description = 'Username'

    def display_avatar_thumbnail(self, obj):
        if obj.provider_avatar:
            return mark_safe(f'<img src="{obj.provider_avatar.url}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />')
        return "No Avatar"
    display_avatar_thumbnail.short_description = 'Avatar'

    def display_avatar(self, obj):
        if obj.provider_avatar:
            return mark_safe(f'<img src="{obj.provider_avatar.url}" width="200" style="border-radius: 8px;" />')
        return "No Avatar uploaded"
    display_avatar.short_description = 'Full View Avatar'

    def display_valid_id(self, obj):
        if obj.valid_id:
            return mark_safe(f'<img src="{obj.valid_id.url}" width="400" style="border-radius: 8px; border: 1px solid #ccc;" />')
        return "No Valid ID uploaded"
    display_valid_id.short_description = 'Submitted Valid ID'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin portal para sa Buy & Sell products.
    """
    list_display = ['name', 'seller', 'price', 'city', 'status', 'display_main_image', 'created_at']
    list_filter = ['status', 'city', 'category']
    search_fields = ['name', 'description', 'seller__user__username']
    
    # Pinapayagan ang admin na i-update ang status direkta mula sa list view
    list_editable = ['status'] 
    
    # In-link ang ProductImageInline para sa gallery support
    inlines = [ProductImageInline]

    def display_main_image(self, obj):
        # Logic para kumuha ng main feature image o first image
        main_img = obj.images.filter(is_feature=True).first() or obj.images.first()
        if main_img and main_img.image:
            return mark_safe(f'<img src="{main_img.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    display_main_image.short_description = 'Main Image'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Admin configuration para sa Service listings.
    """
    list_display = ['name', 'provider', 'price', 'service_city', 'status', 'created_at']
    list_filter = ['status', 'service_city', 'category']
    search_fields = ['name', 'description', 'provider__profile__user__username']
    list_editable = ['status']
    inlines = [ServiceImageInline]


# Simple model registrations
admin.site.register(Profile)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category management na may automatic slug generation para sa SEO.
    """
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'category_type']