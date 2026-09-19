"""
Serializers package for djbcknd app.
Split into separate files per concern; this __init__.py re-exports everything
so that existing code doing `from app.serializers import X` continues to work
without changes.
"""

from .category import CategorySerializer
from .product import ProductImageSerializer, ProductSerializer
from .service import ServiceSerializer, CreateServiceSerializer
from .user import UserSerializer, UserProfileStatusSerializer
from .inquiry import ServiceInquirySerializer
from .notification import NotificationSerializer

__all__ = [
    'CategorySerializer',
    'ProductImageSerializer',
    'ProductSerializer',
    'ServiceSerializer',
    'CreateServiceSerializer',
    'UserSerializer',
    'UserProfileStatusSerializer',
    'ServiceInquirySerializer',
    'NotificationSerializer',
]