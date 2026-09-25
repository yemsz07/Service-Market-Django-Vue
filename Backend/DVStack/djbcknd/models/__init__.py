"""
Models package for djbcknd app.
Split into separate files per concern; this __init__.py re-exports everything
so that existing code doing `from app.models import X` continues to work
without changes, and so Django can still discover every model.
"""
 
from .profile import Profile, ServiceProviderProfile
from .category import Category
from .product import Product, ProductImage
from .service import Service, ServiceImage, ServiceInquiry
from .notification import Notification
from .payment_transaction import PaymentTransaction
 
# Registers the post_save receivers — must be imported so Django connects them.
from . import signals  # noqa: F401
 
__all__ = [
    'Profile',
    'ServiceProviderProfile',
    'Category',
    'Product',
    'ProductImage',
    'Service',
    'ServiceImage',
    'ServiceInquiry',
    'Notification',
    'PaymentTransaction',
]
 