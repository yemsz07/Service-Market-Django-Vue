from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Profile, ServiceProviderProfile, Category, Product, ProductImage, Service, ServiceImage

# ==========================================
# MGA INLINE MODELS (Para sa Maramihang Larawan)
# ==========================================

class ProductImageInline(admin.TabularInline):
    """Pinapakita ang mga larawan ng produkto sa loob mismo ng Product page"""
    model = ProductImage
    extra = 1
    readonly_fields = ['display_image']

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')
        return "No Image"
    display_image.short_description = "Preview"


class ServiceImageInline(admin.TabularInline):
    """Pinapakita ang portfolio images sa loob mismo ng Service page"""
    model = ServiceImage
    extra = 1
    readonly_fields = ['display_image']

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />')
        return "No Image"
    display_image.short_description = "Preview"


# ==========================================
# MGA MAIN ADMIN CUSTOMIZATIONS
# ==========================================

@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    """
    DITO LALABAS ANG MGA REKWISITOS PARA SA PROVDIER APPROVAL.
    Makikita mo agad ang Avatar, Valid ID, at Address para sa mabilis na pag-approve.
    """
    list_display = ['get_username', 'approval_status', 'display_avatar_thumbnail', 'verified_at']
    list_filter = ['approval_status']
    search_fields = ['profile__user__username', 'detailed_address']
    
    # Ginagawang readonly ang mga larawan sa detalye para hindi aksidenteng mabago, pero may preview
    readonly_fields = ['display_avatar', 'display_valid_id']
    
    # Inaayos ang pagkakasunod-sunod sa loob ng edit page
    fieldsets = [
        ('User Info', {'fields': ['profile', 'approval_status', 'verified_at']}),
        ('Sensitibong Detalye (Admin Only)', {'fields': ['detailed_address', 'display_valid_id']}),
        ('Public Info', {'fields': ['display_avatar']}),
    ]

    # Helper methods para sa mga larawan
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
    display_avatar.short_description = 'Provider Profile Picture'

    def display_valid_id(self, obj):
        if obj.valid_id:
            return mark_safe(f'<img src="{obj.valid_id.url}" width="400" style="border-radius: 8px; border: 1px solid #ccc;" />')
        return "No Valid ID uploaded"
    display_valid_id.short_description = 'Submitted Valid ID'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration para sa Buy & Sell"""
    list_display = ['name', 'seller', 'price', 'city', 'status', 'display_main_image', 'created_at']
    list_filter = ['status', 'city', 'category']
    search_fields = ['name', 'description', 'seller__user__username']
    list_editable = ['status'] # Pwede mong gawing SOLD direkta sa listahan nang hindi pumapasok sa loob
    inlines = [ProductImageInline] # Dito papasok yung multiple images sa ilalim

    def display_main_image(self, obj):
        # Kukunin ang feature image, kung wala, kukuha ng kahit anong unang larawan
        main_img = obj.images.filter(is_feature=True).first() or obj.images.first()
        if main_img and main_img.image:
            return mark_safe(f'<img src="{main_img.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    display_main_image.short_description = 'Main Image'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration para sa Services"""
    list_display = ['name', 'provider', 'price', 'service_city', 'status', 'created_at']
    list_filter = ['status', 'service_city', 'category']
    search_fields = ['name', 'description', 'provider__profile__user__username']
    list_editable = ['status']
    inlines = [ServiceImageInline]


# I-register ang mga natitirang simpleng models
admin.site.register(Profile)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)} # Awtomatikong gagawa ng slug habang nagtatype ng name
    list_display = ['name', 'category_type']