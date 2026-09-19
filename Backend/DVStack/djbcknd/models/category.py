from django.db import models


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