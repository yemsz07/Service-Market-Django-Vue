"""Admin configuration for djbcknd app.

Provides custom dashboards, inline image viewers, and bulk actions for
verification.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Category,
    Product,
    ProductImage,
    Profile,
    Service,
    ServiceImage,
    ServiceProviderProfile,
)


# ==========================================
# 📸 INLINES (Manage Images Inside Parent Pages)
# ==========================================


class ProductImageInline(admin.TabularInline):
  """Allows adding and viewing Product gallery images directly inside the Product edit page."""

  model = ProductImage
  extra = 1
  readonly_fields = ('image_preview',)

  @admin.display(description='Preview')
  def image_preview(self, obj):
    if obj.image:
      return format_html(
          '<img src="{}" style="height: 60px; width: 60px; object-fit: cover;'
          ' border-radius: 4px;" />',
          obj.image.url,
      )
    return 'No Image'


class ServiceImageInline(admin.TabularInline):
  """Allows adding and viewing Service gallery images directly inside the Service edit page."""

  model = ServiceImage
  extra = 1
  readonly_fields = ('image_preview',)

  @admin.display(description='Preview')
  def image_preview(self, obj):
    if obj.image:
      return format_html(
          '<img src="{}" style="height: 60px; width: 60px; object-fit: cover;'
          ' border-radius: 4px;" />',
          obj.image.url,
      )
    return 'No Image'


# ==========================================
# 🛡️ 1. SERVICE PROVIDER VERIFICATION DASHBOARD
# ==========================================


@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
  """Custom Admin UI for reviewing and verifying Service Provider applications.

  Includes ID previews, bulk actions, and verification audit trails.
  """

  list_display = (
      'get_username',
      'get_city',
      'approval_status',
      'id_thumbnail',
      'avatar_thumbnail',
      'verified_at',
  )
  list_filter = ('approval_status', 'verified_at')
  search_fields = (
      'profile__user__username',
      'profile__user__email',
      'detailed_address',
  )
  readonly_fields = ('verified_at', 'id_full_preview', 'avatar_full_preview')

  # Custom grouping of form fields in the admin detail view
  fieldsets = (
      ('👤 User Account', {'fields': ('profile',)}),
      (
          '🛡️ Admin Verification Status',
          {'fields': ('approval_status', 'admin_notes', 'verified_at')},
      ),
      (
          '🆔 Identification Document (Admin Only)',
          {'fields': ('valid_id', 'id_full_preview', 'detailed_address')},
      ),
      (
          '🌐 Public Profile Details',
          {'fields': ('provider_avatar', 'avatar_full_preview')},
      ),
  )

  # Custom Admin Actions for quick 1-click approvals/rejections
  actions = ['approve_providers', 'reject_providers']

  # --- Display Helper Methods ---

  @admin.display(description='Username')
  def get_username(self, obj):
    return obj.profile.user.username

  @admin.display(description='City')
  def get_city(self, obj):
    return obj.profile.city or 'N/A'

  @admin.display(description='ID Thumbnail')
  def id_thumbnail(self, obj):
    if obj.valid_id:
      return format_html(
          '<a href="{}" target="_blank" title="Click to view full size">'
          '<img src="{}" style="height: 40px; width: 60px; object-fit: cover;'
          ' border-radius: 4px; border: 1px solid #ddd;" />'
          '</a>',
          obj.valid_id.url,
          obj.valid_id.url,
      )
    return 'No ID Uploaded'

  @admin.display(description='Avatar')
  def avatar_thumbnail(self, obj):
    if obj.provider_avatar:
      return format_html(
          '<img src="{}" style="height: 40px; width: 40px; object-fit: cover;'
          ' border-radius: 50%;" />',
          obj.provider_avatar.url,
      )
    return 'No Avatar'

  @admin.display(description='ID Document Full View')
  def id_full_preview(self, obj):
    if obj.valid_id:
      return format_html(
          '<a href="{}" target="_blank">'
          '<img src="{}" style="max-width: 450px; max-height: 300px;'
          ' border-radius: 8px; border: 1px solid #ccc;" />'
          '</a><br><small style="color: #666;">Click image to open original in a'
          ' new tab.</small>',
          obj.valid_id.url,
          obj.valid_id.url,
      )
    return 'No Government ID Uploaded'

  @admin.display(description='Avatar Full View')
  def avatar_full_preview(self, obj):
    if obj.provider_avatar:
      return format_html(
          '<img src="{}" style="max-width: 150px; max-height: 150px;'
          ' border-radius: 8px;" />',
          obj.provider_avatar.url,
      )
    return 'No Avatar Uploaded'

  # --- Bulk Actions ---

  @admin.action(description='✅ Approve selected Service Providers')
  def approve_providers(self, request, queryset):
    updated_count = 0
    for provider in queryset:
      provider.approval_status = 'APPROVED'
      provider.verified_at = timezone.now()
      provider.save()
      updated_count += 1
    self.message_user(
        request, f'Successfully approved {updated_count} provider(s).'
    )

  @admin.action(description='❌ Reject selected Service Providers')
  def reject_providers(self, request, queryset):
    updated_count = 0
    for provider in queryset:
      provider.approval_status = 'REJECTED'
      provider.verified_at = None
      provider.save()
      updated_count += 1
    self.message_user(request, f'Rejected {updated_count} provider(s).')


# ==========================================
# 👤 2. USER PROFILE MANAGEMENT
# ==========================================


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  list_display = (
      'get_username',
      'get_email',
      'city',
      'contact_number',
      'created_at',
  )
  search_fields = ('user__username', 'user__email', 'city', 'contact_number')
  list_filter = ('created_at', 'city')

  @admin.display(description='Username')
  def get_username(self, obj):
    return obj.user.username

  @admin.display(description='Email')
  def get_email(self, obj):
    return obj.user.email


# ==========================================
# 🏷️ 3. CATEGORIES MANAGEMENT
# ==========================================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'category_type', 'slug')
  list_filter = ('category_type',)
  search_fields = ('name',)
  prepopulated_fields = {'slug': ('name',)}


# ==========================================
# 🛒 4. BUY & SELL TAB (Products)
# ==========================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = (
      'name',
      'seller_username',
      'price',
      'city',
      'status',
      'created_at',
  )
  list_filter = ('status', 'category', 'created_at')
  search_fields = ('name', 'description', 'city', 'seller__user__username')
  inlines = [ProductImageInline]

  @admin.display(description='Seller')
  def seller_username(self, obj):
    return obj.seller.user.username


# ==========================================
# 🛠️ 5. SERVICES TAB (Services)
# ==========================================


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
  list_display = (
      'name',
      'provider_username',
      'price',
      'service_city',
      'status',
      'created_at',
  )
  list_filter = ('status', 'category', 'created_at')
  search_fields = (
      'name',
      'description',
      'service_city',
      'provider__profile__user__username',
  )
  inlines = [ServiceImageInline]

  @admin.display(description='Provider')
  def provider_username(self, obj):
    return obj.provider.profile.user.username