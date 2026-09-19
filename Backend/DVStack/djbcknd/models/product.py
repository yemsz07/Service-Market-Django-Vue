from django.db import models

from .category import Category
from .profile import Profile


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